"""Public API for goban-style-qr."""

from goban_style_qr.api import generate_qr_image, make_qr_matrix, merge_render_options, resolve_error_correction, save_qr_image
from goban_style_qr.config import BoardTheme, LogoOptions, QRCodeOptions, RenderOptions
from goban_style_qr.presets import get_render_preset, list_render_presets
from goban_style_qr.renderers import GobanRenderer, QRRenderer

__all__ = [
    "BoardTheme",
    "GobanRenderer",
    "LogoOptions",
    "QRCodeOptions",
    "QRRenderer",
    "RenderOptions",
    "generate_qr_image",
    "get_render_preset",
    "list_render_presets",
    "make_qr_matrix",
    "merge_render_options",
    "resolve_error_correction",
    "save_qr_image",
]
