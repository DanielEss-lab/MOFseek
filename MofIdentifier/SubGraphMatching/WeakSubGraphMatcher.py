import time

from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator
import igraph


# This subgraph matcher will IGNORE HYDROGEN and will call a match for
# molecules of equal size that are subgraph isomorphic in either direction


def igraph_from_molecule(molecule):
    graph = igraph.Graph()
    for atom in molecule.atoms:
        if atom.type_symbol != 'H':
            graph.add_vertex(atom.label, element=atom.type_symbol)
    for atom in molecule.atoms:
        if atom.type_symbol != 'H':
            for bonded_atom in atom.bondedAtoms:
                if bonded_atom.type_symbol != 'H':
                    while not bonded_atom.is_in_unit_cell():
                        bonded_atom = bonded_atom.original
                    if bonded_atom in molecule.atoms:
                        graph.add_edge(atom.label, bonded_atom.label)
    return graph


def mol_near_isomorphic(mol_1, mol_2):
    graph_a = igraph_from_molecule(mol_1)
    graph_b = igraph_from_molecule(mol_2)
    return graphs_near_isomorphic(graph_a, graph_b)


def graphs_near_isomorphic(graph_a, graph_b):
    if graph_a.vcount() != graph_b.vcount():
        return False
    match = (graph_a.subisomorphic_vf2(graph_b, node_compat_fn=SubGraphMatcher.vertices_are_equal)
             or graph_b.subisomorphic_vf2(graph_a, node_compat_fn=SubGraphMatcher.vertices_are_equal))
    return match


if __name__ == '__main__':
    bond_creator = XyzBondCreator()

    ligand = XyzReader.read_xyz('../ligandsWildcards/M6_node.xyz')
    bond_creator.connect_atoms(ligand)
    molecule = XyzReader.read_xyz('../ligandsWildcards/contains_m6_node_good.xyz')
    bond_creator.connect_atoms(molecule)

    before_read_time = time.time()
    print("Ligand in mof: ")
    print(mol_near_isomorphic(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)
