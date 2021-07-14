import os
import platform
import subprocess

from GUI import Settings
from MofIdentifier.fileIO import MoleculeWriter


def make_and_open(molecule):
    path = Settings.get_download_filepath()
    MoleculeWriter.write_one(molecule, path)
    open_file(os.path.join(path, molecule.label))


def make_and_see(molecule):
    path = Settings.get_download_filepath()
    MoleculeWriter.write_one(molecule, path)
    see_file(os.path.join(path, molecule.label))


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