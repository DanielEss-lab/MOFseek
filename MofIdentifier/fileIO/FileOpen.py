import os
import platform
import subprocess
from pathlib import Path

from GUI import Settings
from MofIdentifier.Molecules import MOF
from MofIdentifier.fileIO import MoleculeWriter, CifWriter


def make_and_open(molecule):
    path = make_file(molecule)
    full_path = os.path.join(path, molecule.label)
    extension = full_path[full_path.rfind('.'):]
    if Settings.open_app_filepath[extension] == "":
        open_file(full_path)
    else:
        open_file_with_app(full_path, Settings.open_app_filepath[extension])


def make_and_see(molecule):
    path = make_file(molecule)
    see_file(str(Path(os.path.join(path, molecule.label))))


def make_and_see_text(text, name):
    path = str(Path(os.path.join(Settings.get_download_filepath(), name)))
    with open(path, 'w') as f:
        f.write(text)
    see_file(path)


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


def open_file_with_app(file_path, app_path):
    subprocess.call([app_path, file_path])


def see_file(filepath):
    if platform.system() == "Windows":  # Windows
        subprocess.Popen(["explorer", "/select,", filepath])
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", "-R", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])


if __name__ == '__main__':
    file_path = r'/Users/davidl/Downloads/ABAVIJ_clean.cif'
    app_path = r'/Applications/CCDC/Mercury/mercury.app/Contents/MacOS/mercury'  # C:\Windows\system32
    open_file_with_app(file_path, app_path)
