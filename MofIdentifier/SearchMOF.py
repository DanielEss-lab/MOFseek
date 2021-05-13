import os
import CifReader
import XyzReader
import SubGraphMatcher
from pathlib import Path
from XyzBondCreator import XyzBondCreator


def ligands_list():
    bond_creator = XyzBondCreator()

    Benzene = XyzReader.read_xyz(Path(__file__).parent / "ligandsWildcards/BenzeneWildCard.xyz")
    bond_creator.connect_atoms(Benzene)

    CO2_1 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/CO2_1.xyz')
    bond_creator.connect_atoms(CO2_1)

    H2O_1 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/H2O_1.xyz')
    bond_creator.connect_atoms(H2O_1)

    H2O_2 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/H2O_2.xyz')
    bond_creator.connect_atoms(H2O_2)

    HSO4_1 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/HSO4_1.xyz')
    bond_creator.connect_atoms(HSO4_1)

    HSO4_2 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/HSO4_2.xyz')
    bond_creator.connect_atoms(HSO4_2)

    M6_node = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/M6_node.xyz')
    bond_creator.connect_atoms(M6_node)

    SO4_1 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/SO4_1.xyz')
    bond_creator.connect_atoms(SO4_1)

    SO4_2 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/SO4_2.xyz')
    bond_creator.connect_atoms(SO4_2)

    SO4_3 = XyzReader.read_xyz(Path(__file__).parent / 'ligandsWildcards/SO4_3.xyz')
    bond_creator.connect_atoms(SO4_3)

    ligands = {Benzene, CO2_1, H2O_1, H2O_2, HSO4_1, HSO4_2, M6_node, SO4_1, SO4_2, SO4_3}

    return ligands


def read_Cif(file_path):
    # Change the directory
    os.chdir(file_path)

    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".cif"):
            mof = CifReader.read_mof(file)
            print(mof)
            print("Elements in mof:", *mof.elementsPresent)
            search_ligands(mof)
            print("Ligand in mof:", *mof.ligandsPresent, "\n")


def search_ligands(mof):
    bond_creator = XyzBondCreator()
    bond_creator.connect_atoms(mof)
    # if find_ligand_in_mof returns true, then put the ligand into mof.ligandsPresent set
    for ligand in ligands_list():
        if SubGraphMatcher.find_ligand_in_mof(ligand, mof):
            mof.ligandsPresent.add(Path(ligand.label).stem)


if __name__ == '__main__':
    # Folder Path
    user_path = input("Enter a folder path that has .cif files: (Example: \\Users\shers\Desktop\Chem\structure_10143)\n")
    # path = "\'" + user_path
    read_Cif(user_path)
