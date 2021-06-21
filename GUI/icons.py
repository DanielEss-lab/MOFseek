import platform

if platform.system() == 'Windows':  # Windows
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 1
elif platform.system() == 'Darwin':  # macOS
    SEE_ICON = "reveal"
    OPEN_ICON = "open"
    EDIT_ICON = "\u270e"
    LINK_CURSOR = 'pointinghand'
    PROGRESS_SPEED = 512
else:  # linux variants
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 1
