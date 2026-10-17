from pathlib import Path

import pytest

from scripts.render_walkthrough import render


def test_render_refuses_existing_output_without_touching_it(tmp_path: Path) -> None:
    output = tmp_path / "existing.mp4"
    output.write_bytes(b"keep this recording")
    with pytest.raises(FileExistsError):
        render(tmp_path, output)
    assert output.read_bytes() == b"keep this recording"


def test_render_refuses_missing_recording_before_starting_encoder(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        render(tmp_path, tmp_path / "new.mp4")
    assert list(tmp_path.iterdir()) == []


def test_render_requires_static_mode_caption_before_starting_encoder(tmp_path: Path) -> None:
    (tmp_path / "walkthrough.webm").write_bytes(b"not a decoded video")
    (tmp_path / "recording.json").write_text(
        '{"chapters":[{"seconds":0}],"browser_errors":[],"mode":"fixture"}'
    )
    with pytest.raises(FileNotFoundError, match="caption"):
        render(tmp_path, tmp_path / "new.mp4")
    assert not (tmp_path / "new.mp4").exists()
