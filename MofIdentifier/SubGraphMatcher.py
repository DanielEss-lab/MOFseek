import networkx.algorithms.isomorphism as iso
import networkx as nx
from MofIdentifier import XyzReader, CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator


def nodes_are_equal(a, b):
    a_elem = a['element']
    b_elem = b['element']
    return a_elem == b_elem


def find_ligand_in_mof(ligand, mof):
    lGraph = nx.Graph()
    for atom in ligand.atoms:
        lGraph.add_node(atom, element=atom.type_symbol)
    for atom in ligand.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
                assert (bonded_atom in ligand.atoms)
            lGraph.add_edge(atom, bonded_atom)
    mGraph = nx.Graph()
    for atom in mof.atoms:
        mGraph.add_node(atom, element=atom.type_symbol)
    for atom in mof.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
                assert(bonded_atom in mof.atoms)
            mGraph.add_edge(atom, bonded_atom)
    graph_matcher = iso.GraphMatcher(mGraph, lGraph)
    print("match without testing element:", graph_matcher.subgraph_is_isomorphic())
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=iso.categorical_node_match(['element'], [None]))
    print("match with generated element test:", graph_matcher.subgraph_is_isomorphic())
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=nodes_are_equal)
    print("match with hand-made element test:", graph_matcher.subgraph_is_isomorphic())
    mof_contains_ligand = graph_matcher.subgraph_is_isomorphic()
    return mof_contains_ligand


if __name__ == '__main__':
    carbon = XyzReader.read_xyz('SingleCarbon.xyz')
    bond_creator = XyzBondCreator()
    bond_creator.connect_atoms(carbon)
    benzene = XyzReader.read_xyz('BenzeneBase.xyz')
    bond_creator.connect_atoms(benzene)
    solitary_benzene = XyzReader.read_xyz('Benzene.xyz')
    bond_creator.connect_atoms(solitary_benzene)
    mof_808 = CifReader.read_mof('smod7-pos-1.cif')
    bond_creator = MofBondCreator(mof_808)
    bond_creator.connect_atoms()

    print("\nCarbon in Carbon: (expected True)")
    find_ligand_in_mof(carbon, carbon)

    print("\nCarbon in Benzene: (expected True)")
    find_ligand_in_mof(carbon, benzene)

    print("\nCarbon in mof: (expected True)")
    find_ligand_in_mof(carbon, mof_808)

    print("\nBenzene in Benzene: (expected True)")
    find_ligand_in_mof(benzene, benzene)

    print("\nBenzene in mof: (expected True)")
    find_ligand_in_mof(benzene, mof_808)

    print("\nSolitaryBenzene in mof: (expected False)")
    find_ligand_in_mof(solitary_benzene, mof_808)
