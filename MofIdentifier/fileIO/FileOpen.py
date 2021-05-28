import os
import platform
import subprocess


def open_file(path):
    os.startfile(path)


def see_file(path):
    if platform.system() == "Windows":
        subprocess.Popen(["explorer", "/select,", path])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])