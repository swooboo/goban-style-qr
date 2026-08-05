from __future__ import annotations

import io

from PIL import Image

from goban_style_qr.web import create_app


def test_web_index_loads() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Generate PNG" in response.data
    assert b"Preset" in response.data


def test_web_generation_returns_preview_and_download_link() -> None:
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (16, 16), (255, 0, 0, 128))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/generate",
        data={
            "data": "https://example.com/browser",
            "preset": "example",
            "error_correction": "H",
            "white_stone_ratio": "0.1",
            "seed": "7",
            "logo": (buffer, "logo.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert "image" in data
    assert len(data["image"]) > 0
