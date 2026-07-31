from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from goban_style_qr import LogoOptions, QRCodeOptions, RenderOptions, generate_qr_image, make_qr_matrix, resolve_error_correction


def test_resolve_error_correction_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        resolve_error_correction("x")


def test_generated_image_size_matches_matrix_and_options() -> None:
    render_options = RenderOptions(module_size=10, border_modules=2)
    matrix = make_qr_matrix("https://example.com", options=QRCodeOptions(error_correction="Q"))
    image = generate_qr_image(
        "https://example.com",
        qr_options=QRCodeOptions(error_correction="Q"),
        render_options=render_options,
    )

    expected_size = (len(matrix) + 2 * render_options.border_modules) * render_options.module_size
    assert image.size == (expected_size, expected_size)


def test_white_stone_layout_is_deterministic_for_same_seed() -> None:
    options = RenderOptions(white_stone_ratio=0.2, seed=7)
    first = generate_qr_image("seeded-output", render_options=options)
    second = generate_qr_image("seeded-output", render_options=options)

    assert first.tobytes() == second.tobytes()


def test_logo_is_embedded_inside_reserved_center(tmp_path: Path) -> None:
    logo_path = tmp_path / "logo.png"
    logo = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    for x in range(4, 16):
        for y in range(4, 16):
            logo.putpixel((x, y), (220, 40, 40, 255))
    logo.save(logo_path)

    image = generate_qr_image(
        "logo-test",
        logo_options=LogoOptions(image_path=logo_path, reserved_modules=7, padding_modules=0.5),
    )

    center = image.getpixel((image.width // 2, image.height // 2))
    assert center[0] > center[1]
    assert center[0] > center[2]
