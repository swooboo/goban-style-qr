from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image, ImageChops

from goban_style_qr import (
    LogoOptions,
    QRCodeOptions,
    RenderOptions,
    generate_qr_image,
    get_render_preset,
    list_render_presets,
    make_qr_matrix,
    resolve_error_correction,
)

REFERENCE_IMAGE = Path("/home/runner/work/goban-style-qr/goban-style-qr/tests/fixtures/example-reference.png")


def test_resolve_error_correction_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        resolve_error_correction("x")


def test_render_presets_include_example_default() -> None:
    assert list_render_presets() == ("example", "compact", "high-contrast")
    assert get_render_preset().stone_scale == 1.0
    assert get_render_preset().white_stone_ratio == pytest.approx(0.25)


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


def test_logo_is_embedded_inside_reserved_center_from_bytes(tmp_path: Path) -> None:
    logo_path = tmp_path / "logo.png"
    logo = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    for x in range(4, 16):
        for y in range(4, 16):
            logo.putpixel((x, y), (220, 40, 40, 255))
    logo.save(logo_path)

    image = generate_qr_image(
        "logo-test",
        logo_options=LogoOptions(image_bytes=logo_path.read_bytes(), reserved_modules=7, padding_modules=0.5),
    )

    center = image.getpixel((image.width // 2, image.height // 2))
    assert center[0] > center[1]
    assert center[0] > center[2]


def test_example_preset_matches_reference_image() -> None:
    expected = Image.open(REFERENCE_IMAGE)
    actual = generate_qr_image("https://example.com/reference", render_options=get_render_preset("example"))

    difference = ImageChops.difference(actual.convert("RGBA"), expected.convert("RGBA"))
    assert difference.getbbox() is None


def test_example_preset_output_decodes() -> None:
    payload = "https://example.com/scannable"
    image = generate_qr_image(payload, render_options=get_render_preset("example"))
    detector = cv2.QRCodeDetector()
    decoded, _, _ = detector.detectAndDecode(np.array(image.convert("RGB")))

    assert decoded == payload
