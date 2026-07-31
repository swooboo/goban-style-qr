from __future__ import annotations

import argparse
from pathlib import Path

from goban_style_qr.api import generate_qr_image
from goban_style_qr.config import BoardTheme, LogoOptions, QRCodeOptions, RenderOptions


def build_parser() -> argparse.ArgumentParser:
    """Build the goban-style-qr CLI parser."""

    parser = argparse.ArgumentParser(description="Generate goban-style QR code images.")
    parser.add_argument("data", help="Text or URL to encode")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="H")
    parser.add_argument("--module-size", type=int, default=18)
    parser.add_argument("--border-modules", type=int, default=4)
    parser.add_argument("--stone-scale", type=float, default=0.88)
    parser.add_argument("--grid-line-width", type=int, default=2)
    parser.add_argument("--white-stone-ratio", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--background-color", default="#DDBB77")
    parser.add_argument("--grid-color", default="#8A613A")
    parser.add_argument("--black-stone-color", default="#111111")
    parser.add_argument("--white-stone-color", default="#F6F1E7")
    parser.add_argument("--logo", default=None)
    parser.add_argument("--logo-reserved-modules", type=int, default=9)
    parser.add_argument("--logo-padding-modules", type=float, default=1.0)
    parser.add_argument("--logo-size-ratio", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the goban-style-qr CLI."""

    args = build_parser().parse_args(argv)
    render_options = RenderOptions(
        module_size=args.module_size,
        border_modules=args.border_modules,
        stone_scale=args.stone_scale,
        grid_line_width=args.grid_line_width,
        white_stone_ratio=args.white_stone_ratio,
        seed=args.seed,
        theme=BoardTheme(
            background_color=args.background_color,
            grid_color=args.grid_color,
            black_stone_color=args.black_stone_color,
            white_stone_color=args.white_stone_color,
        ),
    )
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
        render_options=render_options,
        logo_options=logo_options,
    )
    image.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
