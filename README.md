# goban-style-qr

Create QR codes that look like positions from the game of Go (Baduk/Goban).

## Installation

```bash
pip install goban-style-qr
```

For local development:

```bash
pip install -e .[dev]
```

## Python API

```python
from goban_style_qr import LogoOptions, QRCodeOptions, RenderOptions, generate_qr_image

image = generate_qr_image(
    "https://example.com",
    qr_options=QRCodeOptions(error_correction="H"),
    render_options=RenderOptions(
        module_size=18,
        border_modules=4,
        white_stone_ratio=0.12,
        seed=42,
    ),
    logo_options=LogoOptions("examples/logo.png", reserved_modules=9, padding_modules=0.5),
)
image.save("goban-qr.png")
```

## Command line usage

```bash
goban-style-qr "https://example.com" goban-qr.png \
  --white-stone-ratio 0.12 \
  --seed 42 \
  --logo examples/logo.png
```

## Public API

- `generate_qr_image(data, ...)` renders a PIL image.
- `make_qr_matrix(data, ...)` exposes the generated QR matrix.
- `RenderOptions`, `QRCodeOptions`, `BoardTheme`, and `LogoOptions` configure rendering.
- `GobanRenderer` provides the default Goban-style renderer and can be replaced later with other renderers.

## Example images

- `examples/basic.png`
- `examples/with_logo.png`

## Testing

```bash
pytest
```
