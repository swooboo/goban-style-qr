from __future__ import annotations

import argparse
import base64
import io
import json
from html import escape

from flask import Flask, jsonify, request

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


def _resolve_logo_options() -> tuple[LogoOptions | None, str]:
    upload = request.files.get("logo")
    clear_logo = request.form.get("clear_logo") == "on"

    if upload and upload.filename:
        image_bytes = upload.read()
        mime = upload.content_type or "image/png"
        b64 = base64.b64encode(image_bytes).decode("ascii")
        return (
            LogoOptions(
                image_bytes=image_bytes,
                reserved_modules=9,
                padding_modules=1.0,
                size_ratio=1.0,
            ),
            f"data:{mime};base64,{b64}",
        )

    if clear_logo:
        return None, ""

    logo_data_uri = request.form.get("logo_data", "")
    if not logo_data_uri:
        return None, ""

    try:
        _header, b64_part = logo_data_uri.split(",", 1)
        image_bytes = base64.b64decode(b64_part)
    except Exception:
        return None, ""

    return (
        LogoOptions(
            image_bytes=image_bytes,
            reserved_modules=9,
            padding_modules=1.0,
            size_ratio=1.0,
        ),
        logo_data_uri,
    )


def _generate_payload() -> dict[str, str]:
    data = request.form.get("data", _DEFAULT_DATA).strip() or _DEFAULT_DATA
    preset = request.form.get("preset", "example")
    white_ratio = _parse_optional_float(request.form.get("white_stone_ratio"))
    seed = _parse_optional_int(request.form.get("seed"))
    error_correction = request.form.get("error_correction", "H")
    logo_options, logo_data_uri = _resolve_logo_options()

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
    return {
        "image_data": encoded,
        "logo_data_uri": logo_data_uri,
    }


def create_app() -> Flask:
    """Create a browser-based QR generation app."""

    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return _render_page()

    @app.post("/")
    def generate_page() -> str:
        payload = _generate_payload()
        return _render_page(image_data=payload["image_data"], logo_data_uri=payload["logo_data_uri"])

    @app.post("/generate")
    def generate() -> tuple[dict[str, str], int]:
        return jsonify(_generate_payload()), 200

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
    logo_hidden_field = ''
    if logo_data_uri:
        logo_preview_markup = f'''
          <div class="logo-state">
            <img class="logo-preview" src="{logo_data_uri}" alt="Logo preview" />
            <label class="remove-logo"><input type="checkbox" name="clear_logo" /> Remove logo</label>
          </div>'''
        logo_hidden_field = f'<input type="hidden" name="logo_data" value="{logo_data_uri}" />'

    result_hidden_attr = " hidden" if image_data is None else ""
    result_src = f"data:image/png;base64,{image_data}" if image_data else ""
    preset_js_data = _build_preset_js_data()

    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Goban Style QR</title>
    <style>
      :root {{ color-scheme: light; }}
      * {{ box-sizing: border-box; }}
      body {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; margin: 0; background: linear-gradient(180deg, #f8f0df 0%, #efe4cf 100%); color: #1f1b16; }}
      main {{ max-width: 64rem; margin: 0 auto; padding: 1.5rem; }}
      .page-header {{ margin-bottom: 1rem; }}
      .page-header h1 {{ margin: 0 0 .35rem; font-size: clamp(2rem, 4vw, 2.8rem); }}
      .layout {{ display: grid; gap: 1rem; align-items: start; }}
      @media (min-width: 900px) {{ .layout {{ grid-template-columns: minmax(0, 26rem) minmax(0, 1fr); }} .result {{ position: sticky; top: 1rem; }} }}
      form, .result {{ background: rgba(255,255,255,.94); border: 1px solid rgba(109,76,47,.12); border-radius: 1.25rem; padding: 1.25rem; box-shadow: 0 12px 30px rgba(67,45,23,.10); margin-bottom: 1rem; backdrop-filter: blur(6px); }}
      label {{ display: block; font-weight: 600; margin-top: .9rem; }}
      input, select, button {{ width: 100%; font: inherit; padding: .8rem .9rem; margin-top: .35rem; border-radius: .85rem; border: 1px solid #d8c5a8; background: #fffdf9; }}
      input:focus, select:focus {{ outline: 2px solid #a06b3b; outline-offset: 1px; }}
      button {{ background: linear-gradient(180deg, #7a5533 0%, #5f4027 100%); color: white; border: 0; cursor: pointer; font-weight: 700; box-shadow: 0 8px 18px rgba(109,76,47,.22); }}
      button[disabled] {{ opacity: .7; cursor: progress; }}
      img {{ width: 100%; height: auto; display: block; margin-top: 1rem; border-radius: 1rem; background: #e0c090; }}
      a {{ color: #6d4c2f; font-weight: 700; text-decoration: none; }}
      .hint {{ color: #5b534b; font-size: .95rem; margin: 0; }}
      .status {{ min-height: 1.25rem; margin-top: .75rem; color: #5b534b; font-size: .95rem; }}
      .result[hidden] {{ display: none; }}
      .result-header {{ display: flex; gap: 1rem; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }}
      .result-header h2 {{ margin: 0 0 .35rem; }}
      .download-link {{ display: inline-flex; align-items: center; justify-content: center; padding: .85rem 1rem; border-radius: .85rem; background: #f3e4cf; border: 1px solid #d8c5a8; white-space: nowrap; }}
      .logo-state {{ margin-top: .5rem; }}
      .logo-preview {{ max-width: 6rem; height: auto; margin-top: .5rem; border-radius: .5rem; background: repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 0 0 / 12px 12px; }}
      .remove-logo {{ display: flex; align-items: center; gap: .4rem; font-weight: normal; margin-top: .4rem; }}
      .remove-logo input {{ width: auto; margin: 0; padding: 0; }}
    </style>
  </head>
  <body>
    <main>
      <header class=\"page-header\">
        <h1>Goban Style QR</h1>
        <p class=\"hint\">Generate a Go-board style QR code without leaving the page, then save the image right from the preview.</p>
      </header>
      <div class=\"layout\">
        <form id=\"qr-form\" method=\"post\" enctype=\"multipart/form-data\">
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

          <button type=\"submit\" id=\"generate-button\">Generate PNG</button>
          <p class=\"status\" id=\"status\" aria-live=\"polite\"></p>
        </form>
        <section class=\"result\" id=\"result\"{result_hidden_attr}>
          <div class=\"result-header\">
            <div>
              <h2>Preview</h2>
              <p class=\"hint\">Your QR code stays on this page so it is easy to save or share.</p>
            </div>
            <a class=\"download-link\" download=\"goban-style-qr.png\" href=\"{result_src}\">Download PNG</a>
          </div>
          <img id=\"result-image\" alt=\"Generated goban QR code\" src=\"{result_src}\" />
        </section>
      </div>
    </main>
    <script>
      (function () {{
        var presets = {preset_js_data};
        var presetEl = document.getElementById('preset');
        var ratioEl = document.getElementById('white_stone_ratio');
        var seedEl = document.getElementById('seed');
        var formEl = document.getElementById('qr-form');
        var buttonEl = document.getElementById('generate-button');
        var statusEl = document.getElementById('status');
        var resultEl = document.getElementById('result');
        var resultImageEl = document.getElementById('result-image');
        var downloadEl = resultEl ? resultEl.querySelector('.download-link') : null;
        var persistedLogoData = {json.dumps(logo_data_uri)};
        var hiddenLogoEl = formEl.querySelector('input[name="logo_data"]');
        if (hiddenLogoEl) hiddenLogoEl.remove();
        function updatePlaceholders() {{
          var d = presets[presetEl.value] || {{}};
          ratioEl.placeholder = d.white_stone_ratio || '';
          seedEl.placeholder = d.seed || '';
        }}
        function buildFormData() {{
          var formData = new FormData(formEl);
          formData.delete('logo_data');
          var fileInputEl = formEl.querySelector('input[name="logo"]');
          var hasSelectedFile = fileInputEl && fileInputEl.files && fileInputEl.files.length > 0;
          if (!hasSelectedFile && persistedLogoData) {{
            formData.set('logo_data', persistedLogoData);
          }}
          return formData;
        }}
        async function handleSubmit(event) {{
          event.preventDefault();
          buttonEl.disabled = true;
          statusEl.textContent = 'Generating PNG…';
          try {{
            var response = await fetch('/generate', {{ method: 'POST', body: buildFormData() }});
            if (!response.ok) throw new Error('Request failed');
            var payload = await response.json();
            var dataUrl = 'data:image/png;base64,' + payload.image_data;
            resultImageEl.src = dataUrl;
            downloadEl.href = dataUrl;
            var fileInputEl = formEl.querySelector('input[name="logo"]');
            var logoStateEl = formEl.querySelector('.logo-state');
            persistedLogoData = payload.logo_data_uri || '';
            if (fileInputEl) {{
              fileInputEl.value = '';
            }}
            if (logoStateEl) {{
              if (persistedLogoData) {{
                var previewEl = logoStateEl.querySelector('.logo-preview');
                if (previewEl) previewEl.src = persistedLogoData;
              }} else {{
                logoStateEl.remove();
              }}
            }}
            resultEl.hidden = false;
            resultEl.scrollIntoView({{ block: 'start', behavior: 'smooth' }});
            statusEl.textContent = 'Done.';
          }} catch (_error) {{
            statusEl.textContent = 'Could not generate the image. Please try again.';
          }} finally {{
            buttonEl.disabled = false;
          }}
        }}
        presetEl.addEventListener('change', updatePlaceholders);
        formEl.addEventListener('submit', handleSubmit);
        updatePlaceholders();
      }})();
    </script>
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
