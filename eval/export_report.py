"""Export unchanged measurements with explicit removal of workstation metadata."""

import argparse
import hashlib
from pathlib import Path

from .contracts import EvaluationReport


def export_report(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        raise ValueError("export_requires_distinct_destination")
    raw = source.read_bytes()
    report = EvaluationReport.model_validate_json(raw)
    redacted: list[str] = []
    for key in ("runtime_root", "lease_owner"):
        if key in report.provenance:
            report.provenance.pop(key)
            redacted.append("provenance." + key)
    manifest = report.provenance.get("manifest")
    if isinstance(manifest, str) and (
        Path(manifest).is_absolute() or "\\" in manifest or ".." in Path(manifest).parts
    ):
        report.provenance.pop("manifest")
        redacted.append("provenance.manifest")
    snapshot = report.provenance.get("snapshot")
    if isinstance(snapshot, dict) and "path" in snapshot:
        snapshot.pop("path")
        redacted.append("provenance.snapshot.path")
    report.provenance["publication_export"] = {
        "source_report_sha256": hashlib.sha256(raw).hexdigest(),
        "redacted_fields": [field for field in redacted],
        "measurements_changed": False,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as stream:
        stream.write(report.model_dump_json(indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    export_report(args.source, args.destination)


if __name__ == "__main__":
    main()
