import os
from pathlib import Path

from MofIdentifier.fileIO import XyzReader, SmilesReader


def get_mol_from_file(filepath):
    if filepath.endswith(".xyz"):
        return XyzReader.get_molecule(filepath)
    elif filepath.endswith(".smiles"):
        return SmilesReader.mol_from_file(filepath)
    else:
        return None


def get_mol_from_string(string, name):
    if len(string.split('\n')) > 1:
        return XyzReader.get_molecule_from_string(string, name)
    else:
        return SmilesReader.mol_from_str(string, name)


def get_all_mols_from_directory(filepath):
    mols = []
    # Change the directory
    original_path = os.getcwd()
    os.chdir(filepath)

    for file in os.listdir(filepath):
        # Check whether file is in valid format
        if file.endswith(".xyz") or file.endswith(".smiles"):
            try:
                mol_filepath = Path(file).resolve()
                mol = get_mol_from_file(str(mol_filepath))
                mols.append(mol)
            except Exception:
                print("Error reading file: ", file)
                print(Exception)
    # Return to original directory
    os.chdir(original_path)
    return mols

if __name__ == '__main__':
    mol = get_mol_from_file(r'/Users/davidl/Desktop/Work/Esslab-P66/Analysis/input/MOM.xyz')
    print(mol.elementsPresent)