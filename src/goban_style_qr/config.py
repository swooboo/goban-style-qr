from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias

ColorValue: TypeAlias = str | tuple[int, int, int] | tuple[int, int, int, int]
ErrorCorrectionLevel: TypeAlias = Literal["L", "M", "Q", "H"]
PresetName: TypeAlias = Literal["example", "compact", "high-contrast"]


@dataclass(frozen=True)
class BoardTheme:
    """Colors used by a board renderer."""

    background_color: ColorValue = "#E0C090"
    grid_color: ColorValue = "#C0A080"
    black_stone_color: ColorValue = "black"
    white_stone_color: ColorValue = "#F8F8F8"


@dataclass(frozen=True)
class LogoOptions:
    """Options for embedding a centered logo."""

    image_path: str | Path | None = None
    image_bytes: bytes | None = None
    reserved_modules: int = 9
    padding_modules: float = 1.0
    size_ratio: float = 1.0


@dataclass(frozen=True)
class RenderOptions:
    """Options that control board rendering."""

    module_size: int = 24
    border_modules: int = 4
    stone_scale: float = 1.0
    grid_line_width: int = 2
    white_stone_ratio: float = 0.25
    seed: int | None = 42
    theme: BoardTheme = field(default_factory=BoardTheme)


@dataclass(frozen=True)
class QRCodeOptions:
    """Options used when generating the QR matrix."""

    error_correction: ErrorCorrectionLevel = "H"
