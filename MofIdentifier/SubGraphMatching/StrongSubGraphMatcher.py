import time

from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator
import igraph


def igraph_from_molecule(molecule):
    graph = igraph.Graph()
    for atom in molecule.atoms:
        graph.add_vertex(atom.label, element=atom.type_symbol)
    for atom in molecule.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
            if bonded_atom in molecule.atoms:
                graph.add_edge(atom.label, bonded_atom.label)
    return graph


def mol_are_isomorphic(mol_1, mol_2):
    graph_a = mol_1.get_graph()
    graph_b = mol_2.get_graph()
    match = graph_a.isomorphic_vf2(graph_b, node_compat_fn=SubGraphMatcher.vertices_are_equal)
    return match


def graphs_are_isomorphic(graph_a, graph_b):
    return graph_a.isomorphic_vf2(graph_b, node_compat_fn=SubGraphMatcher.vertices_are_equal)


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