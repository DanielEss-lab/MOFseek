from pathlib import Path

from MofIdentifier.DAO import SBUDAO, LigandDAO, MOFDAO
from MofIdentifier.fileIO import CifReader, LigandReader


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


def refresh_active_collections():
    delete_all()
    add_test_mofs(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\GUI\mofsForGui_temp')))
    add_test_ligands(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands')))


if __name__ == '__main__':
    refresh_active_collections()
    print(SBUDAO.get_num_sbus())
