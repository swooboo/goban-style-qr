from __future__ import annotations

import argparse
import base64
import io
import json
from html import escape

from flask import Flask, request

from goban_style_qr.api import generate_qr_image, merge_render_options
from goban_style_qr.cli import PRESET_CHOICES
from goban_style_qr.config import LogoOptions, QRCodeOptions
from goban_style_qr.presets import get_render_preset, list_render_presets

_DEFAULT_DATA = "https://example.com"


def _build_preset_js_data() -> str:
    """Return a JSON object mapping preset names to their default field values."""
    data = {}
    for name in list_render_presets():
        opts = get_render_preset(name)
        data[name] = {
            "white_stone_ratio": str(opts.white_stone_ratio),
            "seed": str(opts.seed) if opts.seed is not None else "",
        }
    return json.dumps(data)


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
        clear_logo = request.form.get("clear_logo") == "on"

        logo_data_uri = ""
        logo_options = None

        if upload and upload.filename:
            image_bytes = upload.read()
            mime = upload.content_type or "image/png"
            b64 = base64.b64encode(image_bytes).decode("ascii")
            logo_data_uri = f"data:{mime};base64,{b64}"
            logo_options = LogoOptions(
                image_bytes=image_bytes,
                reserved_modules=9,
                padding_modules=1.0,
                size_ratio=1.0,
            )
        elif not clear_logo:
            logo_data_uri = request.form.get("logo_data", "")
            if logo_data_uri:
                try:
                    _header, b64_part = logo_data_uri.split(",", 1)
                    image_bytes = base64.b64decode(b64_part)
                    logo_options = LogoOptions(
                        image_bytes=image_bytes,
                        reserved_modules=9,
                        padding_modules=1.0,
                        size_ratio=1.0,
                    )
                except Exception:
                    logo_data_uri = ""

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
        image_bytes_out = io.BytesIO()
        image.save(image_bytes_out, format="PNG")
        encoded = base64.b64encode(image_bytes_out.getvalue()).decode("ascii")
        return _render_page(
            data=data,
            preset=preset,
            error_correction=error_correction,
            white_stone_ratio="" if white_ratio is None else str(white_ratio),
            seed="" if seed is None else str(seed),
            image_data=encoded,
            logo_data_uri=logo_data_uri,
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
    logo_data_uri: str = "",
) -> str:
    preset_options = "".join(
        f'<option value="{name}"{" selected" if name == preset else ""}>{name.title()}</option>'
        for name in PRESET_CHOICES
    )

    logo_preview_markup = ""
    logo_hidden_field = ""
    if logo_data_uri:
        logo_preview_markup = f"""
          <img class=\"logo-preview\" src=\"{logo_data_uri}\" alt=\"Logo preview\" />
          <label class=\"remove-logo\"><input type=\"checkbox\" name=\"clear_logo\" /> Remove logo</label>"""
        logo_hidden_field = f'<input type="hidden" name="logo_data" value="{logo_data_uri}" />'

    image_markup = ""
    scroll_script = ""
    if image_data:
        image_markup = f"""
      <section class=\"result\" id=\"result\">
        <h2>Preview</h2>
        <img alt=\"Generated goban QR code\" src=\"data:image/png;base64,{image_data}\" />
        <p><a download=\"goban-style-qr.png\" href=\"data:image/png;base64,{image_data}\">Download PNG</a></p>
      </section>"""
        scroll_script = "<script>document.getElementById('result').scrollIntoView({block:'start'});</script>"

    preset_js_data = _build_preset_js_data()

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
      form, .result {{ background: white; border-radius: 1rem; padding: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,.08); margin-bottom: 1rem; }}
      label {{ display: block; font-weight: 600; margin-top: .9rem; }}
      input, select, button {{ width: 100%; font: inherit; padding: .8rem; margin-top: .35rem; box-sizing: border-box; }}
      button {{ background: #6d4c2f; color: white; border: 0; border-radius: .75rem; cursor: pointer; }}
      img {{ width: 100%; height: auto; display: block; margin-top: 1rem; border-radius: .75rem; background: #e0c090; }}
      a {{ color: #6d4c2f; font-weight: 600; }}
      .hint {{ color: #5b534b; font-size: .95rem; }}
      .logo-preview {{ max-width: 6rem; height: auto; margin-top: .5rem; border-radius: .5rem; background: repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 0 0 / 12px 12px; }}
      .remove-logo {{ display: flex; align-items: center; gap: .4rem; font-weight: normal; margin-top: .4rem; }}
      .remove-logo input {{ width: auto; margin: 0; padding: 0; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Goban Style QR</h1>
      <p class=\"hint\">Generate a Go-board style QR code from your Android browser.</p>
      <form method=\"post\" enctype=\"multipart/form-data\">
        {logo_hidden_field}
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
        <input id=\"white_stone_ratio\" name=\"white_stone_ratio\" inputmode=\"decimal\" value=\"{escape(white_stone_ratio)}\" />

        <label for=\"seed\">Random seed (optional override)</label>
        <input id=\"seed\" name=\"seed\" inputmode=\"numeric\" value=\"{escape(seed)}\" />

        <label for=\"logo\">Transparent logo (optional)</label>
        <input id=\"logo\" type=\"file\" name=\"logo\" accept=\"image/png,image/webp,image/jpeg\" />{logo_preview_markup}

        <button type=\"submit\">Generate PNG</button>
      </form>
      {image_markup}
    </main>
    <script>
      (function () {{
        var presets = {preset_js_data};
        var presetEl = document.getElementById('preset');
        var ratioEl = document.getElementById('white_stone_ratio');
        var seedEl = document.getElementById('seed');
        function updatePlaceholders() {{
          var d = presets[presetEl.value] || {{}};
          ratioEl.placeholder = d.white_stone_ratio || '';
          seedEl.placeholder = d.seed || '';
        }}
        presetEl.addEventListener('change', updatePlaceholders);
        updatePlaceholders();
      }})();
    </script>
    {scroll_script}
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
