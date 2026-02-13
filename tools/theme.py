from langchain_core.tools import tool


@tool
async def change_theme(
    theme_mode: str = None,
    accent_color: str = None,
) -> dict:
    """Change the app's visual theme or accent color.

    Use this when user asks to:
    - Switch to dark mode, light mode, or system default
    - Change the accent/brand color of the app

    Parameters:
    - theme_mode: "dark", "light", or "system" (optional)
    - accent_color: one of "green", "blue", "purple", "red", "orange", "teal", "pink", "black", "white" (optional)

    At least one parameter must be provided.
    """
    VALID_MODES = ("dark", "light", "system")
    VALID_COLORS = ("green", "blue", "purple", "red", "orange", "teal", "pink", "black", "white")

    actions = []

    if theme_mode and theme_mode.lower() in VALID_MODES:
        actions.append({"type": "change_theme", "value": theme_mode.lower()})

    if accent_color and accent_color.lower() in VALID_COLORS:
        actions.append({"type": "change_accent", "value": accent_color.lower()})

    if not actions:
        return {
            "success": False,
            "error": f"Invalid parameters. theme_mode must be one of {VALID_MODES}, accent_color must be one of {VALID_COLORS}.",
        }

    return {"success": True, "actions": actions}
