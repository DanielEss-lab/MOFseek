import networkx.algorithms.isomorphism as iso
import networkx as nx
from MofIdentifier import XyzReader, CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator


def find_ligand_in_mof(ligand, mof):
    lGraph = nx.Graph()
    for atom in ligand.atoms:
        lGraph.add_node(atom.type_symbol, element=atom.type_symbol)
    for atom in ligand.atoms:
        for bonded_atom in atom.bondedAtoms:
            if not bonded_atom.isInUnitCell:
                lGraph.add_node(atom.type_symbol, element=atom.type_symbol)
            lGraph.add_edge(atom, bonded_atom)
    mGraph = nx.Graph()
    for atom in mof.atoms:
        mGraph.add_node(atom.type_symbol, element=atom.type_symbol)
    for atom in mof.atoms:
        for bonded_atom in atom.bondedAtoms:
            mGraph.add_edge(atom, bonded_atom)
    graph_matcher = iso.GraphMatcher(mGraph, lGraph)
    print("match without testing element:", graph_matcher.subgraph_is_isomorphic())
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=iso.categorical_node_match(['element'], [None]))
    print("match with generated element test:", graph_matcher.subgraph_is_isomorphic())
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=lambda a, b: a['element'] == b['element'])
    print("match with lambda element test:", graph_matcher.subgraph_is_isomorphic())
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
    find_ligand_in_mof(benzene, benzene)  # This is the problem statement

    print("\nBenzene in mof: (expected True)")
    find_ligand_in_mof(carbon, benzene)

    print("\nSolitaryBenzene in mof: (expected False)")
    find_ligand_in_mof(carbon, solitary_benzene)
