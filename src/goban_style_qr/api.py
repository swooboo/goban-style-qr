from __future__ import annotations

from dataclasses import replace
from typing import Any, Sequence

import qrcode
from PIL import Image

from goban_style_qr.config import LogoOptions, QRCodeOptions, RenderOptions
from goban_style_qr.presets import get_render_preset
from goban_style_qr.renderers import GobanRenderer, QRRenderer

_ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def resolve_error_correction(level: str) -> int:
    """Resolve a human-friendly QR error correction level."""

    normalized = level.upper()
    try:
        return _ERROR_CORRECTION_MAP[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported error correction level: {level}") from exc



def make_qr_matrix(data: str, *, options: QRCodeOptions | None = None) -> Sequence[Sequence[bool]]:
    """Build a QR matrix for *data*."""

    options = options or QRCodeOptions()
    qr = qrcode.QRCode(
        version=None,
        error_correction=resolve_error_correction(options.error_correction),
        box_size=1,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.get_matrix()



def merge_render_options(base: RenderOptions, **overrides: Any) -> RenderOptions:
    """Create a new ``RenderOptions`` with a small set of overrides applied."""

    theme_overrides = overrides.pop("theme", None)
    theme = replace(base.theme, **theme_overrides) if theme_overrides else base.theme
    valid_overrides = {key: value for key, value in overrides.items() if value is not None}
    return replace(base, theme=theme, **valid_overrides)



def generate_qr_image(
    data: str,
    *,
    qr_options: QRCodeOptions | None = None,
    render_options: RenderOptions | None = None,
    logo_options: LogoOptions | None = None,
    renderer: QRRenderer | None = None,
) -> Image.Image:
    """Generate a goban-style QR code image for *data*."""

    matrix = make_qr_matrix(data, options=qr_options)
    return (renderer or GobanRenderer()).render(
        matrix,
        render_options=render_options or get_render_preset(),
        logo_options=logo_options,
    )



def save_qr_image(image: Image.Image, destination: str) -> None:
    """Save a rendered QR image to *destination*."""

    image.save(destination)
