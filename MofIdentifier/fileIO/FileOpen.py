import os
import platform
import subprocess


def open_file(filepath):
    if platform.system() == 'Windows':  # Windows
        os.startfile(filepath)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filepath))
    else:  # linux variants
        subprocess.call(('xdg-open', filepath))


def see_file(filepath):
    if platform.system() == "Windows":  # Windows
        subprocess.Popen(["explorer", "/select,", filepath])
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", "-R", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])