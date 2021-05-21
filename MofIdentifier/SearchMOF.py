import os
import time

from MofIdentifier.fileIO import CifReader, SmilesReader, LigandReader
from MofIdentifier.SubGraphMatching import SubGraphMatcher
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
        if file_name_in_directory.endswith(".xyz") or file_name_in_directory.endswith(".txt"):
            for l_name in ligand_names:
                if file_name_in_directory == l_name:
                    ligands.append(
                        LigandReader.get_mol_from_file(str(Path(__file__).parent / "ligandsWildcards") + "/" + l_name))
                    ligands_found += 1
    if ligands_found < len(ligand_names):
        raise Exception('Did not find all ligands')
    return ligands


def repeat_get_all_mofs_in_directory(mofs_path):
    # list of mofs that has specific ligands
    mofs = []
    # Change the directory
    while True:
        try:
            CifReader.get_all_mofs_in_directory(mofs_path)
        except OSError:
            print(OSError)
            mofs_path = get_mof_path_from_console_input
            continue
        else:
            break

    return mofs


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
    # user_path = get_mof_path_from_console_input()
    # ligand_file_names = get_ligand_list_from_console_input()
    # print('loading mofs and ligands from files...')
    # ligands = read_ligands_from_files(ligand_file_names)
    # mofs = repeat_get_all_mofs_in_directory(user_path)
    # print('Filtering for subgraph isomorphism...')
    # good_mofs = SubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
    # mof_names = map(lambda x: x.label, good_mofs)
    # print(*ligand_file_names, " present in the following file(s):")
    # print(*mof_names, sep="\n")
    user_path = get_mof_path_from_console_input()
    start_time = time.time()
    print('loading mofs and ligands from files...')
    ligands = [SmilesReader.mol_from_str('C1=NNN=N1')]
    mofs = CifReader.get_all_mofs_in_directory(user_path)
    print('Filtering for subgraph isomorphism...')
    good_mofs = SubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
    mof_names = map(lambda x: x.label, good_mofs)
    end_time = time.time()
    print("C1=NNN=N1 present in the following file(s):")
    print(*mof_names, sep="\n")
    time_taken = int(end_time - start_time)
    print('Time taken to search: {} seconds ({} minutes)', time_taken, round(time_taken/60))
