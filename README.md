# goban-style-qr

Create QR codes that look like positions from the game of Go (Baduk/Goban).

The default renderer now aims to match the original prototype more closely: full circular stones, warm wood tones, a visible grid, and a deterministic white-stone layout that still preserves QR readability.

## Installation

```bash
pip install goban-style-qr
```

For local development and tests:

```bash
pip install -e .[dev]
```

## Python API

```python
from goban_style_qr import LogoOptions, QRCodeOptions, generate_qr_image, get_render_preset

image = generate_qr_image(
    "https://example.com",
    qr_options=QRCodeOptions(error_correction="H"),
    render_options=get_render_preset("example"),
    logo_options=LogoOptions(image_path="examples/logo.png", reserved_modules=9, padding_modules=1.0),
)
image.save("goban-qr.png")
```

## Presets

The library ships with a few opinionated presets:

- `example` - default prototype-inspired look
- `compact` - smaller output for tighter layouts
- `high-contrast` - lower white-stone density with a sharper board palette

You can start from a preset and override individual settings in the CLI or your own code.

## Command line usage

```bash
goban-style-qr "https://example.com" goban-qr.png --preset example
```

Optional overrides still work:

```bash
goban-style-qr "https://example.com" goban-qr.png \
  --preset example \
  --white-stone-ratio 0.15 \
  --seed 42 \
  --logo examples/logo.png
```

## Browser UI for Android or other mobile browsers

Run the lightweight web app locally or on a small host:

```bash
goban-style-qr-web --host 0.0.0.0 --port 8000
```

Then open `http://<your-host>:8000` from your Android browser. The web app uses the same Python rendering engine and presets as the library and CLI, supports text/URL input, optional logo upload, and PNG download.

For a simple first deployment, use the command above on a small VPS or a platform that can run a Python web process.

### Deploy on Railway

1. Fork or push the repo to your GitHub account.
2. Go to [railway.com](https://railway.com) → **New Project** → **Deploy from GitHub repo** → select your repo.
3. Railway auto-detects the `Dockerfile` and builds the image.
4. Under **Settings → Networking**, click **Generate Domain** to get a public URL.

No environment variables are required. Railway injects `PORT` automatically and the container reads it at startup.

To run the image locally with Docker:

```bash
docker build -t goban-style-qr .
docker run -p 8000:8000 -e PORT=8000 goban-style-qr
```

## Example images

- `examples/basic.png`
- `examples/with_logo.png`

## Testing

```bash
pytest
```

The test suite covers:

- deterministic rendering behavior
- preset defaults
- browser generation flow
- decode-based scannability with OpenCV
- visual regression against a reference image
