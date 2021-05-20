import time

from MofIdentifier import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator
import igraph


# This subgraph matcher will IGNORE HYDROGEN and will call a match for
# molecules of equal size that are subgraph isomorphic in either direction


def vertices_are_equal(g1, g2, i1, i2):
    return SubGraphMatcher.vertices_are_equal(g1, g2, i1, i2)


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


def find_ligand_in_mof(ligand, mof):
    lGraph = igraph_from_molecule(ligand)
    if len(lGraph.clusters()) != 1:
        raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input file '
                        'and try again.')
    mGraph = igraph_from_molecule(mof)
    mof_contains_ligand = mGraph.subisomorphic_vf2(lGraph, node_compat_fn=vertices_are_equal)
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
    return SubGraphMatcher.mof_has_all_ligands(mof_graph, ligand_graphs)


def mol_near_isomorphic(mol_1, mol_2):
    graph_a = igraph_from_molecule(mol_1)
    graph_b = igraph_from_molecule(mol_2)
    return graphs_near_isomorphic(graph_a, graph_b)


def graphs_near_isomorphic(graph_a, graph_b):
    if graph_a.vcount() != graph_b.vcount():
        return False
    match = (graph_a.subisomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)
             or graph_b.subisomorphic_vf2(graph_a, node_compat_fn=vertices_are_equal))
    return match


def name_molecules_from_set(molecules, mol_set):  # Can operate on anything with .atoms and .label (ie sbus, Ligands)
    not_present_molecules = []
    present_molecules = []
    set_graphs = {mol: igraph_from_molecule(mol) for mol in mol_set}
    for molecule in molecules:
        mol_graph = igraph_from_molecule(molecule)
        if does_assign_label_from_set(molecule, mol_graph, mol_set, set_graphs):
            present_molecules.append(molecule)
        else:
            not_present_molecules.append(molecule)
    return not_present_molecules, present_molecules


def does_assign_label_from_set(molecule, mol_graph, mol_set, set_graphs):
    for mol_from_set in mol_set:
        if graphs_near_isomorphic(mol_graph, set_graphs[mol_from_set]):
            molecule.label = mol_from_set.label
            return True
    return False


if __name__ == '__main__':
    bond_creator = XyzBondCreator()

    ligand = XyzReader.read_xyz('ligandsWildcards/M6_node.xyz')
    bond_creator.connect_atoms(ligand)
    molecule = XyzReader.read_xyz('ligandsWildcards/contains_M6_node_good.xyz')
    bond_creator.connect_atoms(molecule)

    before_read_time = time.time()
    print("Ligand in mof: ")
    print(mol_near_isomorphic(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)
