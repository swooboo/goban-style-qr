from __future__ import annotations

import argparse
import base64
import io
from html import escape

from flask import Flask, request

from goban_style_qr.api import generate_qr_image, merge_render_options
from goban_style_qr.cli import PRESET_CHOICES
from goban_style_qr.config import LogoOptions, QRCodeOptions
from goban_style_qr.presets import get_render_preset

_DEFAULT_DATA = "https://example.com"


def create_app() -> Flask:
    """Create a browser-based QR generation app."""

    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return _render_page()

    @app.post("/")
    def generate() -> str:
        data = request.form.get("data", _DEFAULT_DATA).strip() or _DEFAULT_DATA
        preset = request.form.get("preset", "example")
        white_ratio = _parse_optional_float(request.form.get("white_stone_ratio"))
        seed = _parse_optional_int(request.form.get("seed"))
        error_correction = request.form.get("error_correction", "H")
        upload = request.files.get("logo")

        logo_options = None
        if upload and upload.filename:
            logo_options = LogoOptions(
                image_bytes=upload.read(),
                reserved_modules=9,
                padding_modules=1.0,
                size_ratio=1.0,
            )

        render_options = merge_render_options(
            get_render_preset(preset),
            white_stone_ratio=white_ratio,
            seed=seed,
        )
        image = generate_qr_image(
            data,
            qr_options=QRCodeOptions(error_correction=error_correction),
            render_options=render_options,
            logo_options=logo_options,
        )
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        encoded = base64.b64encode(image_bytes.getvalue()).decode("ascii")
        return _render_page(
            data=data,
            preset=preset,
            error_correction=error_correction,
            white_stone_ratio="" if white_ratio is None else str(white_ratio),
            seed="" if seed is None else str(seed),
            image_data=encoded,
        )

    return app


app = create_app()



def _parse_optional_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)



def _parse_optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)



def _render_page(
    *,
    data: str = _DEFAULT_DATA,
    preset: str = "example",
    error_correction: str = "H",
    white_stone_ratio: str = "",
    seed: str = "",
    image_data: str | None = None,
) -> str:
    preset_options = "".join(
        f'<option value="{name}"{" selected" if name == preset else ""}>{name.title()}</option>'
        for name in PRESET_CHOICES
    )
    image_markup = ""
    if image_data:
        image_markup = f"""
        <section class=\"result\">
          <h2>Preview</h2>
          <img alt=\"Generated goban QR code\" src=\"data:image/png;base64,{image_data}\" />
          <p><a download=\"goban-style-qr.png\" href=\"data:image/png;base64,{image_data}\">Download PNG</a></p>
        </section>
        """

    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Goban Style QR</title>
    <style>
      body {{ font-family: sans-serif; margin: 0; background: #f7f1e3; color: #1f1b16; }}
      main {{ max-width: 42rem; margin: 0 auto; padding: 1rem; }}
      form, .result {{ background: white; border-radius: 1rem; padding: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,.08); }}
      label {{ display: block; font-weight: 600; margin-top: .9rem; }}
      input, select, button {{ width: 100%; font: inherit; padding: .8rem; margin-top: .35rem; box-sizing: border-box; }}
      button {{ background: #6d4c2f; color: white; border: 0; border-radius: .75rem; }}
      img {{ width: 100%; height: auto; display: block; margin-top: 1rem; border-radius: .75rem; background: #e0c090; }}
      a {{ color: #6d4c2f; font-weight: 600; }}
      .hint {{ color: #5b534b; font-size: .95rem; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Goban Style QR</h1>
      <p class=\"hint\">Generate a Go-board style QR code from your Android browser.</p>
      <form method=\"post\" enctype=\"multipart/form-data\">
        <label for=\"data\">Text or URL</label>
        <input id=\"data\" name=\"data\" value=\"{escape(data)}\" required />

        <label for=\"preset\">Preset</label>
        <select id=\"preset\" name=\"preset\">{preset_options}</select>

        <label for=\"error_correction\">Error correction</label>
        <select id=\"error_correction\" name=\"error_correction\">
          <option value=\"L\"{" selected" if error_correction == "L" else ""}>L</option>
          <option value=\"M\"{" selected" if error_correction == "M" else ""}>M</option>
          <option value=\"Q\"{" selected" if error_correction == "Q" else ""}>Q</option>
          <option value=\"H\"{" selected" if error_correction == "H" else ""}>H</option>
        </select>

        <label for=\"white_stone_ratio\">White stone ratio (optional override)</label>
        <input id=\"white_stone_ratio\" name=\"white_stone_ratio\" inputmode=\"decimal\" value=\"{escape(white_stone_ratio)}\" placeholder=\"preset default\" />

        <label for=\"seed\">Random seed (optional override)</label>
        <input id=\"seed\" name=\"seed\" inputmode=\"numeric\" value=\"{escape(seed)}\" placeholder=\"preset default\" />

        <label for=\"logo\">Transparent logo (optional)</label>
        <input id=\"logo\" type=\"file\" name=\"logo\" accept=\"image/png,image/webp,image/jpeg\" />

        <button type=\"submit\">Generate PNG</button>
      </form>
      {image_markup}
    </main>
  </body>
</html>
"""



def main(argv: list[str] | None = None) -> int:
    """Run the local development web server."""

    import os

    parser = argparse.ArgumentParser(description="Run the Goban Style QR web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    args = parser.parse_args(argv)
    app.run(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
