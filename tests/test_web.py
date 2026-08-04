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
    assert b'id="qr-form"' in response.data
    assert b'id="result" hidden' in response.data
    assert b"fetch('/generate'" in response.data
    assert b"formData.delete('logo_data')" in response.data
    assert b"persistedLogoData" in response.data


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
    payload = response.get_json()
    assert payload is not None
    assert payload["image_data"]
    assert payload["logo_data_uri"].startswith("data:image/")


def test_web_logo_persists_across_submissions() -> None:
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (16, 16), (0, 255, 0, 200))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    buffer.seek(0)

    response1 = client.post(
        "/generate",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
            "logo": (buffer, "logo.png"),
        },
        content_type="multipart/form-data",
    )
    assert response1.status_code == 200
    payload1 = response1.get_json()
    assert payload1 is not None
    logo_data_uri = payload1["logo_data_uri"]
    assert logo_data_uri.startswith("data:image/")

    response2 = client.post(
        "/generate",
        data={
            "data": "https://example.com",
            "preset": "example",
            "error_correction": "H",
            "logo_data": logo_data_uri,
        },
        content_type="multipart/form-data",
    )
    assert response2.status_code == 200
    payload2 = response2.get_json()
    assert payload2 is not None
    assert payload2["image_data"]
    assert payload2["logo_data_uri"] == logo_data_uri


def test_web_clear_logo_removes_persistence() -> None:
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    logo_data_uri = f"data:image/png;base64,{b64}"

    response = client.post(
        "/generate",
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
    payload = response.get_json()
    assert payload is not None
    assert payload["logo_data_uri"] == ""


def test_web_post_root_renders_result_section_for_noscript_fallback() -> None:
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
    assert b"Download PNG" in response.data


def test_web_generate_endpoint_keeps_working_with_persisted_logo_only() -> None:
    app = create_app()
    client = app.test_client()
    logo = Image.new("RGBA", (16, 16), (120, 40, 200, 255))
    buffer = io.BytesIO()
    logo.save(buffer, format="PNG")
    buffer.seek(0)

    first = client.post(
        "/generate",
        data={
            "data": "https://example.com/repeat",
            "preset": "example",
            "error_correction": "H",
            "logo": (buffer, "logo.png"),
        },
        content_type="multipart/form-data",
    )
    assert first.status_code == 200
    payload1 = first.get_json()
    assert payload1 is not None

    second = client.post(
        "/generate",
        data={
            "data": "https://example.com/repeat",
            "preset": "example",
            "error_correction": "H",
            "logo_data": payload1["logo_data_uri"],
        },
        content_type="multipart/form-data",
    )
    assert second.status_code == 200
    payload2 = second.get_json()
    assert payload2 is not None
    assert payload2["logo_data_uri"] == payload1["logo_data_uri"]
    assert payload2["image_data"]
