"""Add recording captions below the uncut browser viewport using local FFmpeg."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def render(root: Path, output: Path) -> None:
    if output.exists() or output.with_suffix(".json").exists():
        raise FileExistsError("Use a fresh output name; recordings are not overwritten.")
    source = root / "walkthrough.webm"
    recording = root / "recording.json"
    if not source.is_file() or not recording.is_file():
        raise FileNotFoundError("A successful recording and its evidence are required.")
    data: dict[str, Any] = json.loads(recording.read_text())
    chapters: list[dict[str, Any]] = data["chapters"]
    if not chapters or data["browser_errors"]:
        raise ValueError("No chapters or browser errors present.")
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("Install FFmpeg, including ffprobe, to render recordings.")
    source_media: dict[str, Any] = json.loads(
        subprocess.check_output(
            [ffprobe, "-v", "error", "-show_format", "-of", "json", str(source)], text=True
        )
    )
    # Playwright can start the page video before the test body clock begins.
    # Align their closing boundary instead of putting captions ahead of actions.
    offset = max(
        0.0, float(source_media["format"]["duration"]) - float(data["captured_wall_seconds"])
    )
    command = [ffmpeg, "-n", "-hide_banner", "-loglevel", "error", "-i", str(source)]
    graph = ["[0:v]pad=iw:ih+100:0:0:color=0x0b1220[v0]"]
    for index, chapter in enumerate(chapters):
        caption = root / f"caption-{index}.png"
        if not caption.is_file():
            raise FileNotFoundError(caption.name)
        command.extend(["-i", str(caption)])
        start = 0 if index == 0 else float(chapter["seconds"]) + offset
        end = (
            float(chapters[index + 1]["seconds"]) + offset if index + 1 < len(chapters) else 100000
        )
        graph.append(
            f"[v{index}][{index + 1}:v]overlay=0:1000:"
            f"enable='gte(t,{start})*lt(t,{end})'[v{index + 1}]"
        )
    command.extend(
        [
            "-filter_complex",
            ";".join(graph),
            "-map",
            f"[v{len(chapters)}]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "25",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-map_metadata",
            "-1",
            "-metadata",
            f"title={data['label']}",
            str(output),
        ]
    )
    subprocess.run(command, check=True)
    probe: dict[str, Any] = json.loads(
        subprocess.check_output(
            [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(output)],
            text=True,
        )
    )
    probe["format"].pop("filename", None)
    evidence = {
        "kind": "Uncut real browser capture with a caption strip below the viewport; no speed change",
        "source_video_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "recording_evidence_sha256": hashlib.sha256(recording.read_bytes()).hexdigest(),
        "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "video_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "mode": data["mode"],
        "source_commit": data["source_commit"],
        "source_dirty": data["source_dirty"],
        "chapters": chapters,
        "media": probe,
        "human_review": "pending",
        "caption_clock_offset_seconds": offset,
    }
    with output.with_suffix(".json").open("x") as file:
        file.write(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                "mode": data["mode"],
                "duration": probe["format"]["duration"],
                "bytes": output.stat().st_size,
                "sha256": evidence["video_sha256"],
            }
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.root, args.output)


if __name__ == "__main__":
    main()
