import os
import platform
from pathlib import Path

from DAO import MOFDAO, SBUDAO, DBConnection, LigandDAO
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
    done_ligands = ['L23_no_S.xyz',
                    'M6_node_alternate.xyz',
                    'SingleMetal.xyz',
                    'SO4_3.xyz',
                    'SO4_2.xyz',
                    'M6_node.xyz',
                    'SO4_1.xyz',
                    'HSO4_2.xyz',
                    'H2O_bonded.xyz',
                    'HSO4_1.xyz',
                    'CO2_1.xyz',
                    'Benzene.smiles',
                    'L23.xyz'
                    ]
    for ligand in ligands:
        if ligand.label in done_ligands:
            continue
        LigandDAO.add_ligand_to_db(ligand)
        print(f'{ligand.label} is done being added')
        done_ligands.append(ligand.label)
    print(done_ligands)


def create_indices():
    DBConnection.cif_collection.create_index("filename", unique="True")
    DBConnection.ligand_collection.create_index("ligand_name", unique="True")
    DBConnection.sbu_collection.create_index("sbu_name", unique="True")


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
        add_all_mofs(str(Path(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143')))
        # add_test_ligands(str(Path(r'/MofIdentifier/ligands')))
        # MOFDAO.add_csv_info('')
    elif platform.system() == 'Darwin':  # macOS
        add_all_mofs(str(Path(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143')))
        add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
        MOFDAO.add_csv_info('/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020.csv')


if __name__ == '__main__':
    # add_test_ligands(str(Path(r'/Users/davidl/Desktop/Work/Esslab-P66/MofIdentifier/ligands')))
    # refresh_active_collections_to_test()
    # fill_db()
    LigandDAO.add_ligand_to_db(LigandReader.get_mol_from_file(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66'
                                                                       r'\MofIdentifier\ligands\BTC.smiles'))))
    print(MOFDAO.get_num_mofs(), "mofs in DB now")
