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
