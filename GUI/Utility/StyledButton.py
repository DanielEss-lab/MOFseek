import tkinter as tk

from GUI import os_specific_settings


def make(parent, text, command, font=None):
    if font is None:
        return tk.Button(parent, text=text, command=command,
                         highlightcolor=os_specific_settings.secondary_color,
                         highlightbackground=os_specific_settings.secondary_color, highlightthickness=1)
    else:
        return tk.Button(parent, text=text, command=command, font=font,
                         highlightcolor=os_specific_settings.secondary_color,
                         highlightbackground=os_specific_settings.secondary_color, highlightthickness=1)
