from __future__ import annotations

import argparse
from pathlib import Path

from goban_style_qr.api import generate_qr_image, merge_render_options
from goban_style_qr.config import LogoOptions, QRCodeOptions
from goban_style_qr.presets import get_render_preset, list_render_presets


PRESET_CHOICES = list_render_presets()



def build_parser() -> argparse.ArgumentParser:
    """Build the goban-style-qr CLI parser."""

    parser = argparse.ArgumentParser(description="Generate goban-style QR code images.")
    parser.add_argument("data", help="Text or URL to encode")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--preset", choices=PRESET_CHOICES, default="example")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="H")
    parser.add_argument("--module-size", type=int, default=None)
    parser.add_argument("--border-modules", type=int, default=None)
    parser.add_argument("--stone-scale", type=float, default=None)
    parser.add_argument("--grid-line-width", type=int, default=None)
    parser.add_argument("--white-stone-ratio", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--background-color", default=None)
    parser.add_argument("--grid-color", default=None)
    parser.add_argument("--black-stone-color", default=None)
    parser.add_argument("--white-stone-color", default=None)
    parser.add_argument("--logo", default=None)
    parser.add_argument("--logo-reserved-modules", type=int, default=9)
    parser.add_argument("--logo-padding-modules", type=float, default=1.0)
    parser.add_argument("--logo-size-ratio", type=float, default=1.0)
    return parser



def build_render_options(args: argparse.Namespace):
    """Build render options from parsed CLI args."""

    return merge_render_options(
        get_render_preset(args.preset),
        module_size=args.module_size,
        border_modules=args.border_modules,
        stone_scale=args.stone_scale,
        grid_line_width=args.grid_line_width,
        white_stone_ratio=args.white_stone_ratio,
        seed=args.seed,
        theme={
            key: value
            for key, value in {
                "background_color": args.background_color,
                "grid_color": args.grid_color,
                "black_stone_color": args.black_stone_color,
                "white_stone_color": args.white_stone_color,
            }.items()
            if value is not None
        },
    )



def main(argv: list[str] | None = None) -> int:
    """Run the goban-style-qr CLI."""

    args = build_parser().parse_args(argv)
    logo_options = None
    if args.logo:
        logo_options = LogoOptions(
            image_path=Path(args.logo),
            reserved_modules=args.logo_reserved_modules,
            padding_modules=args.logo_padding_modules,
            size_ratio=args.logo_size_ratio,
        )

    image = generate_qr_image(
        args.data,
        qr_options=QRCodeOptions(error_correction=args.error_correction),
        render_options=build_render_options(args),
        logo_options=logo_options,
    )
    image.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
