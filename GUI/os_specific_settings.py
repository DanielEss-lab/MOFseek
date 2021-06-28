import platform
import tkinter as tk

if platform.system() == 'Windows':  # Windows
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 32
    mof_outline_color = "#ffffff"
elif platform.system() == 'Darwin':  # macOS
    SEE_ICON = "reveal"
    OPEN_ICON = "open"
    EDIT_ICON = "\u270e"
    LINK_CURSOR = 'pointinghand'
    PROGRESS_SPEED = 32
    mof_outline_color = "#e2e2e2"
else:  # linux variants
    SEE_ICON = "\U0001f4c1"
    OPEN_ICON = "\U0001F441"
    EDIT_ICON = "\U0001F589"
    LINK_CURSOR = 'hand2'
    PROGRESS_SPEED = 1
    mof_outline_color = "#ffffff"

def style_for_platform(style):
    if platform.system() == 'Windows':  # Windows
        pass
    elif platform.system() == 'Darwin':  # macOS
        style.theme_use('clam')  # ('aqua', 'clam', 'alt', 'default', 'classic')
        # style.configure("TButton", bd=4)
        # style.configure("TButton", relief=tk.SOLID)
        # style.configure("TButton", highlightcolor='#000000')
        # style.configure("TButton", highlightbackground='#000000')
        # style.configure("TButton", highlightthickness=3)
        # style.configure("TButton", bg='#ff0000')
    else:  # linux variants
        pass