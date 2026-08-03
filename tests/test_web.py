from __future__ import annotations

import base64
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
        "/",
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
    assert b"data:image/png;base64," in response.data
    assert b"Download PNG" in response.data


def test_web_logo_persists_across_submissions() -> None:
    """Logo uploaded in one POST is round-tripped via hidden field in subsequent POST."""
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (16, 16), (0, 255, 0, 200))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    buffer.seek(0)

    # First POST: upload logo
    response1 = client.post(
        "/",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
            "logo": (buffer, "logo.png"),
        },
        content_type="multipart/form-data",
    )
    assert response1.status_code == 200
    assert b'name="logo_data"' in response1.data
    assert b"Logo preview" in response1.data

    # Extract the logo_data value from the hidden field
    page = response1.data.decode()
    marker = 'name="logo_data" value="'
    start = page.index(marker) + len(marker)
    end = page.index('"', start)
    logo_data_uri = page[start:end]
    assert logo_data_uri.startswith("data:image/")

    # Second POST: no file upload, but hidden field carries logo
    response2 = client.post(
        "/",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
            "logo_data": logo_data_uri,
        },
        content_type="multipart/form-data",
    )
    assert response2.status_code == 200
    assert b"data:image/png;base64," in response2.data
    assert b"Logo preview" in response2.data


def test_web_clear_logo_removes_persistence() -> None:
    """The 'Remove logo' checkbox clears the logo from the next response."""
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    logo_data_uri = f"data:image/png;base64,{b64}"

    response = client.post(
        "/",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
            "logo_data": logo_data_uri,
            "clear_logo": "on",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Logo preview" not in response.data


def test_web_result_section_has_id_for_scroll() -> None:
    """The result section has id='result' for anchor-based scrolling."""
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b'id="result"' in response.data
    assert b"scrollIntoView" in response.data
