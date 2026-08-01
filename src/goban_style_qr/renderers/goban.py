from __future__ import annotations

import io
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageOps

from goban_style_qr.config import LogoOptions, RenderOptions
from goban_style_qr.renderers.base import QRRenderer


@dataclass(frozen=True)
class ReservedArea:
    start_row: int
    end_row: int
    start_column: int
    end_column: int

    def contains(self, row: int, column: int) -> bool:
        return self.start_row <= row < self.end_row and self.start_column <= column < self.end_column

    @property
    def width(self) -> int:
        return self.end_column - self.start_column


class GobanRenderer(QRRenderer):
    """Render QR modules as Go stones on a goban board."""

    def render(
        self,
        matrix: Sequence[Sequence[bool]],
        *,
        render_options: RenderOptions,
        logo_options: LogoOptions | None = None,
    ) -> Image.Image:
        module_count = len(matrix)
        if module_count == 0:
            raise ValueError("QR matrix must not be empty")

        module_size = render_options.module_size
        image_size = (module_count + 2 * render_options.border_modules) * module_size
        image = Image.new("RGBA", (image_size, image_size), render_options.theme.background_color)
        draw = ImageDraw.Draw(image)

        center_offset = render_options.border_modules * module_size + module_size / 2
        grid_end = center_offset + (module_count - 1) * module_size
        for index in range(module_count):
            coordinate = center_offset + index * module_size
            draw.line(
                [(coordinate, center_offset), (coordinate, grid_end)],
                fill=render_options.theme.grid_color,
                width=render_options.grid_line_width,
            )
            draw.line(
                [(center_offset, coordinate), (grid_end, coordinate)],
                fill=render_options.theme.grid_color,
                width=render_options.grid_line_width,
            )

        reserved_area = self._build_reserved_area(module_count, logo_options)
        black_positions: list[tuple[int, int]] = []
        empty_positions: list[tuple[int, int]] = []
        for row_index, row in enumerate(matrix):
            for column_index, value in enumerate(row):
                if reserved_area and reserved_area.contains(row_index, column_index):
                    continue
                if value:
                    black_positions.append((row_index, column_index))
                else:
                    empty_positions.append((row_index, column_index))

        white_count = min(
            len(empty_positions),
            int(len(black_positions) * max(0.0, render_options.white_stone_ratio)),
        )
        randomizer = random.Random(render_options.seed)
        white_positions = randomizer.sample(empty_positions, white_count) if white_count else []

        for row, column in white_positions:
            self._draw_stone(
                draw,
                row=row,
                column=column,
                module_size=module_size,
                border_modules=render_options.border_modules,
                stone_scale=render_options.stone_scale,
                fill=render_options.theme.white_stone_color,
            )

        for row, column in black_positions:
            self._draw_stone(
                draw,
                row=row,
                column=column,
                module_size=module_size,
                border_modules=render_options.border_modules,
                stone_scale=render_options.stone_scale,
                fill=render_options.theme.black_stone_color,
            )

        if logo_options and reserved_area:
            self._paste_logo(image, logo_options, reserved_area, module_size, render_options.border_modules)

        return image

    @staticmethod
    def _build_reserved_area(module_count: int, logo_options: LogoOptions | None) -> ReservedArea | None:
        if logo_options is None:
            return None
        if logo_options.reserved_modules <= 0:
            raise ValueError("logo reserved_modules must be greater than zero")
        size = min(module_count, logo_options.reserved_modules)
        start = (module_count - size) // 2
        end = start + size
        return ReservedArea(start_row=start, end_row=end, start_column=start, end_column=end)

    @staticmethod
    def _draw_stone(
        draw: ImageDraw.ImageDraw,
        *,
        row: int,
        column: int,
        module_size: int,
        border_modules: int,
        stone_scale: float,
        fill: str | tuple[int, int, int] | tuple[int, int, int, int],
    ) -> None:
        diameter = module_size * stone_scale
        radius = diameter / 2
        center_x = (border_modules + column) * module_size + module_size / 2
        center_y = (border_modules + row) * module_size + module_size / 2
        draw.ellipse(
            [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ],
            fill=fill,
        )

    @staticmethod
    def _load_logo(logo_options: LogoOptions) -> Image.Image:
        if logo_options.image_bytes is not None:
            return Image.open(io.BytesIO(logo_options.image_bytes)).convert("RGBA")
        if logo_options.image_path is not None:
            return Image.open(Path(logo_options.image_path)).convert("RGBA")
        raise ValueError("logo options must define image_path or image_bytes")

    @classmethod
    def _paste_logo(
        cls,
        image: Image.Image,
        logo_options: LogoOptions,
        reserved_area: ReservedArea,
        module_size: int,
        border_modules: int,
    ) -> None:
        logo = cls._load_logo(logo_options)
        available_size = max(
            1,
            int((reserved_area.width - 2 * logo_options.padding_modules) * module_size),
        )
        target_size = max(1, int(available_size * logo_options.size_ratio))
        logo = ImageOps.contain(logo, (target_size, target_size), Image.Resampling.LANCZOS)

        left = (border_modules + reserved_area.start_column) * module_size
        top = (border_modules + reserved_area.start_row) * module_size
        width = reserved_area.width * module_size
        offset_x = left + (width - logo.width) // 2
        offset_y = top + (width - logo.height) // 2
        image.paste(logo, (offset_x, offset_y), logo)
