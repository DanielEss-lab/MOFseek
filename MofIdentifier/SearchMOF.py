import os
import CifReader
import XyzReader
import SubGraphMatcher
from pathlib import Path
from XyzBondCreator import XyzBondCreator


def get_ligand_list():
    # An empty list for ligands that user wants to search
    ligands = []

    # User specifies xyz file name - CO2_1.xyz
    user_input = input("Enter a xyz file name: (Example: CO2_1.xyz). If you want to quit, type \"quit\"\n")

    if user_input == "quit":
        exit()

    # Use while loop
    while user_input != "quit":
        ligands.append(user_input)
        print("Enter a xyz file name: (Example: CO2_1.xyz). If you want to quit, type \"quit\"")
        user_input = input()

    print("Searching... \n")

    return ligands


def read_xyzFiles_from_list():
    files = get_ligand_list()

    ligands = []
    bond_creator = XyzBondCreator()

    for file in os.listdir(Path(__file__).parent / "ligandsWildcards"):
        if file.endswith(".xyz"):
            for ligand in files:
                if file == ligand:
                    ligand_xyz = XyzReader.read_xyz(str(Path(__file__).parent / "ligandsWildcards") + "/" + ligand)
                    bond_creator.connect_atoms(ligand_xyz)
                    ligands.append(ligand_xyz)

    return ligands, files


def read_Cif(file_path):
    # list of mofs that has specific ligands
    mofs = []

    # Get ligands from user
    ligands_files, ligands_name = read_xyzFiles_from_list()

    # Change the directory
    os.chdir(file_path)

    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".cif"):
            mof = CifReader.read_mof(file)
            # print(mof)
            # print("Elements in mof:", *mof.elementsPresent)
            search_ligands(mofs, mof, ligands_files)
            # print("Ligand in mof:", *mof.ligandsPresent, "\n")

    print(*ligands_name, "is(are) in the following file(s):")
    print(*mofs, sep=", ")


def search_ligands(mofs, mof, ligands_list):
    bond_creator = XyzBondCreator()
    bond_creator.connect_atoms(mof)
    # if find_ligand_in_mof returns true, then put the mofs into the list
    for ligand in ligands_list:
        if not SubGraphMatcher.find_ligand_in_mof(ligand, mof):
            return
    # Add to set of mofs
    mofs.append(mof.label)


if __name__ == '__main__':
    # Folder Path
    user_path = input("Enter a folder path that has .cif files: (Example: \\Users\shers\Desktop\Chem\structure_10143)\n")
    read_Cif(user_path)
    # read_xyzFiles_from_list()
