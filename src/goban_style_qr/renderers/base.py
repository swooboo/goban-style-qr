from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from PIL import Image

from goban_style_qr.config import LogoOptions, RenderOptions


class QRRenderer(ABC):
    """Base class for QR renderers."""

    @abstractmethod
    def render(
        self,
        matrix: Sequence[Sequence[bool]],
        *,
        render_options: RenderOptions,
        logo_options: LogoOptions | None = None,
    ) -> Image.Image:
        """Render a QR matrix as an image."""
