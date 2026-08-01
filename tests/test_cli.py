from __future__ import annotations

from pathlib import Path

from PIL import Image

from goban_style_qr.cli import main


def test_cli_creates_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "cli.png"

    exit_code = main(["https://example.com", str(output_path), "--preset", "example", "--white-stone-ratio", "0.1", "--seed", "5"])

    assert exit_code == 0
    assert output_path.exists()
    with Image.open(output_path) as image:
        assert image.size[0] == image.size[1]
