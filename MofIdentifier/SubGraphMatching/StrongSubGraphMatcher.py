import time

from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator


if __name__ == '__main__':
    bond_creator = XyzBondCreator()

    ligand = XyzReader.read_xyz('../ligandsWildcards/M6_node.xyz')
    bond_creator.connect_atoms(ligand)
    molecule = XyzReader.read_xyz('../ligandsWildcards/contains_m6_node_good.xyz')
    bond_creator.connect_atoms(molecule)

    before_read_time = time.time()
    print("Ligand in mof: ")
    print(mol_are_isomorphic(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)