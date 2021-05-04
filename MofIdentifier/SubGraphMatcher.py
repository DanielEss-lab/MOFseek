import networkx.algorithms.isomorphism as iso
import networkx as nx
from MofIdentifier import XyzReader, MofReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator


def find_ligand_in_mof(ligand, mof):
    lGraph = nx.Graph()
    for atom in ligand.atoms:
        lGraph.add_node(atom, element=atom.type_symbol)
    for atom in ligand.atoms:
        for bonded_atom in atom.bondedAtoms:
            lGraph.add_edge(atom, bonded_atom)
    mGraph = nx.Graph()
    for atom in mof.atoms:
        mGraph.add_node(atom, element=atom.type_symbol)
    for atom in mof.atoms:
        for bonded_atom in atom.bondedAtoms:
            mGraph.add_edge(atom, bonded_atom)
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=iso.categorical_node_match(['element'], [None]))
    mof_contains_ligand = graph_matcher.subgraph_is_isomorphic()
    return mof_contains_ligand


if __name__ == '__main__':
    ligand = XyzReader.read_xyz('Benzene.xyz')
    bond_creator = XyzBondCreator()
    bond_creator.connect_atoms(ligand)
    mof = MofReader.read_mof('smod7-pos-1.cif')
    bond_creator = MofBondCreator(mof)
    bond_creator.connect_atoms()
    contains_ligand = find_ligand_in_mof(ligand, mof)
    print(contains_ligand)
