import time

from MofIdentifier.SubGraphMatching import SubGraphMatcher, GraphMaker
from MofIdentifier.fileIO import LigandReader
from MofIdentifier.subbuilding import SBUIdentifier

if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    ligand = LigandReader.get_mol_from_file(input('Ligand?'))
    molecule = LigandReader.get_mol_from_file(input('Larger Molecule?'))
    print(SubGraphMatcher.find_ligand_in_mof(ligand, molecule))
    print(SBUIdentifier.split(molecule))
