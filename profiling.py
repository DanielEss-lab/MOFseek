import cProfile

from DAOsAndServices import LigandDAO
from MofIdentifier.fileIO import LigandReader


def action():
    ligand = LigandReader.get_mol_from_file(r'MofIdentifier/ligands/test_resources/snurr_nonsearchable.smiles')
    LigandDAO.add_ligand_to_db(ligand)


if __name__ == '__main__':
    cProfile.run('action()')
