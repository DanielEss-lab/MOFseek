import os
import platform
import subprocess

from GUI import Settings
from MofIdentifier.fileIO import MoleculeWriter, CifWriter
from MofIdentifier.Molecules import MOF


def make_and_open(molecule):
    path = make_file(molecule)
    open_file(os.path.join(path, molecule.label))


def make_and_see(molecule):
    path = make_file(molecule)
    see_file(os.path.join(path, molecule.label))


def make_file(molecule):
    path = Settings.get_download_filepath()
    if not Settings.keep_solvent and isinstance(molecule, MOF.MOF):
        CifWriter.write_without_solvent(molecule, path)
    else:
        MoleculeWriter.write_one(molecule, path)
    return path


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