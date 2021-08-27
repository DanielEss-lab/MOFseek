import platform

if platform.system() == 'Windows':  # Windows
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 32
    secondary_color = "#ffffff"
    SCROLL_DIVISOR = 120
elif platform.system() == 'Darwin':  # macOS
    SEE_ICON = "reveal"
    OPEN_ICON = "open"
    EDIT_ICON = "\u270e"
    LINK_CURSOR = 'pointinghand'
    PROGRESS_SPEED = 32
    secondary_color = "#e2e2e2"
    SCROLL_DIVISOR = 1
else:  # linux variants
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 1
    secondary_color = "#ffffff"
    SCROLL_DIVISOR = 1

def style_for_platform(style):
    if platform.system() == 'Windows':  # Windows
        pass
    elif platform.system() == 'Darwin':  # macOS
        style.theme_use('clam')  # ('aqua', 'clam', 'alt', 'default', 'classic')
    else:  # linux variants
        pass