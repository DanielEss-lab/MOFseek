import time

from MofIdentifier import atom
from MofIdentifier.fileIO import XyzReader
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator
import igraph


def vertices_are_equal(g1, g2, i1, i2):
    elem_1 = g1.vs[i1]['element']
    elem_1 = elem_1[0] if len(elem_1) > 1 and elem_1[1].isnumeric() else elem_1
    elem_2 = g2.vs[i2]['element']
    elem_2 = elem_2[0] if len(elem_2) > 1 and elem_2[1].isnumeric() else elem_2
    result = elem_1 == elem_2 \
             or elem_1 == '*' or elem_2 == '*' \
             or (elem_1 == '%' and atom.isMetal(elem_2)) or (elem_2 == '%' and atom.isMetal(elem_1)) \
             or (elem_1 == '#' and (elem_2 == 'H' or elem_2 == 'C')) or (
                         elem_2 == '#' and (elem_1 == 'H' or elem_1 == 'C'))
    return result


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
        if mol_graph.isomorphic_vf2(set_graphs[mol_from_set], node_compat_fn=vertices_are_equal):
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
    print(mol_are_isomorphic(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)