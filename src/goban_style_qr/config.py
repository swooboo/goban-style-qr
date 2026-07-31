from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias

ColorValue: TypeAlias = str | tuple[int, int, int] | tuple[int, int, int, int]
ErrorCorrectionLevel: TypeAlias = Literal["L", "M", "Q", "H"]


@dataclass(frozen=True)
class BoardTheme:
    """Colors used by a board renderer."""

    background_color: ColorValue = "#DDBB77"
    grid_color: ColorValue = "#8A613A"
    black_stone_color: ColorValue = "#111111"
    white_stone_color: ColorValue = "#F6F1E7"


@dataclass(frozen=True)
class LogoOptions:
    """Options for embedding a centered logo."""

    image_path: str | Path
    reserved_modules: int = 9
    padding_modules: float = 1.0
    size_ratio: float = 1.0


@dataclass(frozen=True)
class RenderOptions:
    """Options that control board rendering."""

    module_size: int = 18
    border_modules: int = 4
    stone_scale: float = 0.88
    grid_line_width: int = 2
    white_stone_ratio: float = 0.0
    seed: int | None = None
    theme: BoardTheme = field(default_factory=BoardTheme)


@dataclass(frozen=True)
class QRCodeOptions:
    """Options used when generating the QR matrix."""

    error_correction: ErrorCorrectionLevel = "H"
