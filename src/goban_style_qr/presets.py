from __future__ import annotations

from dataclasses import replace

from goban_style_qr.config import BoardTheme, PresetName, RenderOptions

_PRESETS: dict[PresetName, RenderOptions] = {
    "example": RenderOptions(),
    "compact": RenderOptions(module_size=18, white_stone_ratio=0.12),
    "high-contrast": RenderOptions(
        theme=BoardTheme(
            background_color="#E9CF96",
            grid_color="#8A613A",
            black_stone_color="#050505",
            white_stone_color="#FFFDF9",
        ),
        module_size=24,
        white_stone_ratio=0.05,
    ),
}


def list_render_presets() -> tuple[PresetName, ...]:
    """Return the available named render presets."""

    return tuple(_PRESETS)



def get_render_preset(name: PresetName = "example") -> RenderOptions:
    """Return a copy of a named render preset."""

    preset = _PRESETS[name]
    return replace(preset, theme=replace(preset.theme))
