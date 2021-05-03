import networkx.algorithms.isomorphism as iso
import networkx as nx
from MofIdentifier import XyzReader, MofReader


def find_ligand_in_mof(ligand, mof):
    lGraph = nx.Graph()
    lGraph.add_nodes_from(ligand.atoms)
    mGraph = nx.Graph()
    mGraph.add_nodes_from(mof.atoms)
    graph_matcher = iso.GraphMatcher(lGraph, mGraph, node_match=iso.categorical_node_match(['element'], [None]))
    mof_contains_ligand = graph_matcher.subgraph_is_isomorphic()
    return mof_contains_ligand


if __name__ == '__main__':
    ligand = XyzReader.read_xyz('Benzene.xyz')
    mof = MofReader.read_mof('smod7-pos-1.cif')
    contains_ligand = find_ligand_in_mof(ligand, mof)
    print(contains_ligand)
