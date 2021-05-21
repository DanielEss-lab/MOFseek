import os

from MofIdentifier.fileIO import XyzReader, SmilesReader


def get_mol_from_file(filepath):
    if filepath.endswith(".xyz"):
        return XyzReader.get_molecule(filepath)
    elif filepath.endswith(".txt"):
        return SmilesReader.mol_from_file(filepath)
    else:
        return None

def get_all_mols_from_directory(filepath):
    mols = []
    # Change the directory
    original_path = os.getcwd()
    os.chdir(filepath)

    for file in os.listdir():
        # Check whether file is in valid format
        if file.endswith(".xyz") or file.endswith(".txt"):
            try:
                mol = get_mol_from_file(file)
                mols.append(mol)
            except Exception:
                print("Error reading file: ", file)
                print(Exception)
    # Return to original directory
    os.chdir(original_path)
    return mols