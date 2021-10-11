import os
import platform
import time
from pathlib import Path

from DAO import MOFDAO, SBUDAO, DBConnection, LigandDAO, DeleteService
from DAO.MOFDatabase import MOFDatabase
from collections import namedtuple
from MofIdentifier.Molecules.MOF import NoMetalException
from MofIdentifier.fileIO import CifReader, LigandReader, MoleculeWriter
from MofIdentifier.fileIO.CifReader import get_mof


def delete_all():
    SBUDAO.delete_all_sbus()
    LigandDAO.delete_all_ligands()
    MOFDAO.delete_all_mofs()


def add_test_mofs(directory):
    mofs = CifReader.get_all_mofs_in_directory(directory)
    # C:\Users\mdavid4\Desktop\Esslab-P66\GUI\mofsForGui_temp
    for mof in mofs:
        MOFDAO.add_mof(mof)


def add_certain_ligands(directory, ligands_to_add):
    ligands = LigandReader.get_all_mols_from_directory(directory)
    # C:\Users\mdavid4\Desktop\Esslab - P66\MofIdentifier\ligands
    for ligand in ligands:
        if ligand.label not in ligands_to_add:
            continue
        LigandDAO.add_ligand_to_db(ligand)


def add_all_ligands(directory):
    ligands = LigandReader.get_all_mols_from_directory(directory)
    for ligand in ligands:
        LigandDAO.add_ligand_to_db(ligand)


def create_indices():
    DBConnection.mof_collection.create_index("filename", unique=True)
    DBConnection.ligand_collection.create_index("ligand_name", unique=True)
    DBConnection.sbu_collection.create_index("sbu_name", unique=True)


def add_all_mofs(mofs_path):
    i = 0
    # Change the directory
    original_path = os.getcwd()
    os.chdir(mofs_path)
    mofs_present = MOFDAO.get_all_names()
    num_present = MOFDAO.get_num_mofs()
    assert (num_present == len(mofs_present))
    for file_name in os.listdir(mofs_path):
        # Check whether file is in text format or not
        if file_name.endswith(".cif"):
            name = file_name[:-4]
            if name in mofs_present:
                continue
            try:
                filepath = Path(file_name).resolve()
                filepath = str(filepath)
                print(f"\n{filepath} will be read now...")
                mof = get_mof(filepath)
                MOFDAO.add_mof(mof)
                i += 1
                if i % 100 == 0:
                    print(f"{i} mofs uploaded")
            except NoMetalException:
                print(f"No metal found in {file_name}. This may happen "
                      f"if the metal is too far away from its neighbors.")
            except Exception as ex:
                print("Error reading file: ", file_name)
                print(ex)
    print(i, "mofs uploaded. Finished!")
    # Return to original directory
    os.chdir(original_path)


def refresh_active_collections_to_test():
    delete_all()
    create_indices()
    if platform.system() == 'Windows':  # Windows
        add_certain_ligands(str(Path(r'/MofIdentifier/ligands')))
        add_all_mofs(str(Path(r'/GUI/mofsForGui_temp')))
        MOFDAO.add_csv_info('')
    elif platform.system() == 'Darwin':  # macOS
        add_certain_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/test_mol')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020_short.csv')
    print_summary()


def refresh_active_collections_to_full():
    delete_all()
    create_indices()
    fill_db()
    print_summary()


def print_summary():
    print(MOFDAO.get_num_mofs(), "mofs in DB now")
    for ligand in LigandDAO.get_ligand_iterator():
        print(f"{ligand.name} in {len(ligand.Mofs)} mofs")


def fill_db():
    if platform.system() == 'Windows':  # Windows
        add_all_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')))
        add_all_mofs(str(Path(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143')))
        MOFDAO.add_csv_info(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020.csv')
    elif platform.system() == 'Darwin':  # macOS
        add_all_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020.csv')


def speed_measure():
    print(MOFDAO.get_num_mofs(), "mofs in DB now")
    start = time.time()
    names = MOFDAO.get_all_names()
    for name in names:
        MOFDAO.get_MOF(name)
    end = time.time()
    print(f'{len(names)} names iterated in {round(end - start, 2)} seconds')
    i = 0
    for name in names:
        if i == 100:
            break
        i += 1
        MOFDAO.get_MOF(name)
    start = time.time()
    print(f'100 objects created in {round(start - end, 2)} seconds')


if __name__ == '__main__':
    # refresh_active_collections_to_test()
    # fill_db()
    # MOFDatabase(MOFDAO.get_MOF('ZUTBUN_clean'))
    # speed_measure()
    refresh_active_collections_to_full()
    # add_certain_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')),
    #                    ['sulfonate.smiles', 'phosphonate.smiles', 'carboxyl.smiles'])
    # print_summary()
    # LigandDAO.delete_unmatched_ligands()
    # add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143')))
    # MOFDAO.add_csv_info(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020.csv')
    # add_test_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands\new_ligands')))
    # DeleteService.delete_mof('DOTYES_clean.cif')
    # MOFDAO.add_mof(CifReader.get_mof(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests'
    #                                           r'\DOTYES_clean.cif'))))
