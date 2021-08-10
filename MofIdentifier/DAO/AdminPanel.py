import os
import platform
from pathlib import Path

from MofIdentifier.DAO import SBUDAO, LigandDAO, MOFDAO
from MofIdentifier.DAO import DBConnection
from MofIdentifier.fileIO import CifReader, LigandReader
from MofIdentifier.fileIO.CifReader import get_mof
from MofIdentifier.fileIO.LigandReader import get_mol_from_file


def delete_all():
    SBUDAO.delete_all_sbus()
    LigandDAO.delete_all_ligands()
    MOFDAO.delete_all_mofs()


def add_test_mofs(directory):
    mofs = CifReader.get_all_mofs_in_directory(directory)
    # C:\Users\mdavid4\Desktop\Esslab-P66\GUI\mofsForGui_temp
    for mof in mofs:
        MOFDAO.add_mof(mof)


def add_test_ligands(directory):
    ligands = LigandReader.get_all_mols_from_directory(directory)
    # C:\Users\mdavid4\Desktop\Esslab - P66\MofIdentifier\ligands
    for ligand in ligands:
        LigandDAO.add_ligand_to_db(ligand)


def create_indices():
    DBConnection.cif_collection.create_index("filename", unique="True")
    DBConnection.ligand_collection.create_index("ligand_name", unique="True")
    DBConnection.sbu_collection.create_index("sbu_name", unique="True")


def add_all_mofs(mofs_path):
    i = 0
    # Change the directory
    original_path = os.getcwd()
    os.chdir(mofs_path)
    for file_name in os.listdir(mofs_path):
        # Check whether file is in text format or not
        if file_name.endswith(".cif"):
            try:
                filepath = Path(file_name).resolve()
                filepath = str(filepath)
                mof = get_mof(filepath)
                MOFDAO.add_mof(mof)
                i += 1
                if i % 100 == 0:
                    print(f"{i} mofs uploaded")
            except Exception as ex:
                print("Error reading file: ", file_name)
                print(ex)
    print(i, "mofs uploaded")
    # Return to original directory
    os.chdir(original_path)


def refresh_active_collections_to_test():
    delete_all()
    create_indices()
    if platform.system() == 'Windows':  # Windows
        add_all_mofs(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\GUI\mofsForGui_temp')))
        add_test_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')))
        MOFDAO.add_csv_info('')
    elif platform.system() == 'Darwin':  # macOS
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/test_mol')))
        add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020_short.csv')


def refresh_active_collections_to_full():
    delete_all()
    create_indices()
    if platform.system() == 'Windows':  # Windows
        add_all_mofs(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\GUI\mofsForGui_temp')))
        add_test_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')))
        MOFDAO.add_csv_info('')
    elif platform.system() == 'Darwin':  # macOS
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143')))
        add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020.csv')


if __name__ == '__main__':
    refresh_active_collections_to_full()
