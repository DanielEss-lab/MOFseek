import time

from MofIdentifier import atom
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


def find_ligand_in_mof(ligand, mof):
    # before_setup_time = time.time()
    lGraph = igraph_from_molecule(ligand)
    if len(lGraph.clusters()) != 1:
        raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input file '
                        'and try again.')
    mGraph = igraph_from_molecule(mof)
    # after_setup_time = time.time()
    mof_contains_ligand = mGraph.subisomorphic_vf2(lGraph, node_compat_fn=vertices_are_equal)
    # end_time = time.time()
    # print('time to make graphs: {}'.format(after_setup_time - before_setup_time))
    # print('time to run VF2: {}'.format(end_time - after_setup_time))
    return mof_contains_ligand


def filter_for_mofs_with_ligands(mofs, ligands):
    ligand_graphs = []
    mofs_containing_ligands = []
    for ligand in ligands:
        lGraph = igraph_from_molecule(ligand)
        if len(lGraph.clusters()) != 1:
            raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input '
                            'file and try again.')
        ligand_graphs.append(lGraph)
    for mof in mofs:
        mGraph = igraph_from_molecule(mof)
        if mof_has_all_ligands(mGraph, ligand_graphs):
            mofs_containing_ligands.append(mof)
    return mofs_containing_ligands


def mof_has_all_ligands(mof_graph, ligand_graphs):
    for lGraph in ligand_graphs:
        mof_contains_ligand = mof_graph.subisomorphic_vf2(lGraph, node_compat_fn=vertices_are_equal)
        if not mof_contains_ligand:
            return False
    return True


def mol_are_isomorphic(mol_1, mol_2):
    graph_a = igraph_from_molecule(mol_1)
    graph_b = igraph_from_molecule(mol_2)
    match = graph_a.isomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)
    return match


def graphs_are_isomorphic(graph_a, graph_b):
    return graph_a.isomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)


if __name__ == '__main__':
    bond_creator = XyzBondCreator()

    ligand = XyzReader.read_xyz('ligandsWildcards/M6_node.xyz')
    bond_creator.connect_atoms(ligand)
    molecule = XyzReader.read_xyz('ligandsWildcards/contains_M6_node_good.xyz')
    bond_creator.connect_atoms(molecule)

    before_read_time = time.time()
    print("Ligand in mof: ")
    print(mol_are_isomorphic(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)