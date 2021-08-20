import os
import platform
import time
from pathlib import Path

from DAO import MOFDAO, SBUDAO, DBConnection, LigandDAO
from DAO.MOFDatabase import MOFDatabase
from MofIdentifier.fileIO import CifReader, LigandReader
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


def add_test_ligands(directory):
    ligands = LigandReader.get_all_mols_from_directory(directory)
    # C:\Users\mdavid4\Desktop\Esslab - P66\MofIdentifier\ligands
    done_ligands = ['BTC.smiles', 'Benzene.smiles', 'PO4.xyz']
    for ligand in ligands:
        if ligand.label in done_ligands:
            continue
        LigandDAO.add_ligand_to_db(ligand)
        done_ligands.append(ligand.label)
    print(done_ligands)


def create_indices():
    DBConnection.cif_collection.create_index("filename", unique=True)
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
        add_all_mofs(str(Path(r'/GUI/mofsForGui_temp')))
        add_test_ligands(str(Path(r'/MofIdentifier/ligands')))
        MOFDAO.add_csv_info('')
    elif platform.system() == 'Darwin':  # macOS
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/test_mol')))
        add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020_short.csv')


def refresh_active_collections_to_full():
    delete_all()
    create_indices()
    fill_db()
    print(MOFDAO.get_num_mofs(), "mofs in DB now")


def fill_db():
    if platform.system() == 'Windows':  # Windows
        # add_all_mofs(str(Path(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143')))
        add_test_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')))
        # MOFDAO.add_csv_info(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020.csv')
    elif platform.system() == 'Darwin':  # macOS
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143')))
        add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
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
    # refresh_active_collections_to_full()
    LigandDAO.delete_unmatched_ligands()