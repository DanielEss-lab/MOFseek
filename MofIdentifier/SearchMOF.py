import os

from MofIdentifier.fileIO import XyzReader, CifReader
from MofIdentifier import SubGraphMatcher
from pathlib import Path


def get_ligand_list_from_console_input():
    # An empty list for ligands that user wants to search
    ligands = []

    # User specifies xyz file name - CO2_1.xyz
    user_input = input("Enter a xyz file name: (Example: CO2_1.xyz). If you want to quit, type \"quit\"\n")

    if user_input == "quit":
        raise SystemExit()  # Exit the code execution immediately

    # Use while loop
    while user_input != "done":
        ligands.append(user_input)
        print("Enter a xyz file name: (Example: CO2_1.xyz). When you're done, type \"done\"")
        user_input = input()

    return ligands


def read_ligands_from_files(ligand_names):
    ligands = []
    ligands_found = 0
    for file_name_in_directory in os.listdir(Path(__file__).parent / "ligandsWildcards"):
        if file_name_in_directory.endswith(".xyz"):
            for ligand_name in ligand_names:
                if file_name_in_directory == ligand_name:
                    ligands.append(
                        XyzReader.get_molecule(str(Path(__file__).parent / "ligandsWildcards") + "/" + ligand_name))
                    ligands_found += 1
    if ligands_found < len(ligand_names):
        raise Exception('Did not find all ligands')
    return ligands


def get_all_mofs_in_directory(mofs_path):
    # list of mofs that has specific ligands
    mofs = []
    # Change the directory
    while True:
        try:
            os.chdir(mofs_path)
        except OSError:
            print(OSError)
            mofs_path = get_mof_path_from_console_input
            continue
        else:
            break

    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".cif"):
            try:
                mof = CifReader.get_mof(file)
                mofs.append(mof)
            except Exception:
                print("Error reading file: ", file)
                print(Exception)
    return mofs


def mof_contains_ligands(mof, ligands_list):
    # if find_ligand_in_mof returns true, then put the mofs into the list
    for ligand in ligands_list:
        if not SubGraphMatcher.find_ligand_in_mof(ligand, mof):
            return False
    return True


def get_mof_path_from_console_input():
    prompt = "Enter a folder path that has .cif files: (Example: \\\\Users\\shers\\Desktop\\Chem\\structure_10143)\n"
    path = input(prompt)
    if path == "quit":
        raise SystemExit()  # Exit the code execution immediately

    while not is_valid_path(path):
        print("Invalid folder path: please try again or type \"quit\" to exit")
        path = input(prompt)
        if path == "quit":
            raise SystemExit()  # Exit the code execution immediately
    return path


def is_valid_path(user_path):
    return os.path.exists(user_path)


if __name__ == '__main__':
    # Folder Path
    user_path = get_mof_path_from_console_input()
    ligand_file_names = get_ligand_list_from_console_input()
    print('loading mofs and ligands from files...')
    ligands = read_ligands_from_files(ligand_file_names)
    mofs = get_all_mofs_in_directory(user_path)
    print('Filtering for subgraph isomorphism...')
    good_mofs = SubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
    mof_names = map(lambda x: x.label, good_mofs)
    print(*ligand_file_names, " present in the following file(s):")
    print(*mof_names, sep="\n")
    # read_xyzFiles_from_list()
