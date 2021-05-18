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
        or (elem_1 == '#' and (elem_2 == 'H' or elem_2 == 'C')) or (elem_2 == '#' and (elem_1 == 'H' or elem_1 == 'C'))
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


def are_isomorphic(mol_1, mol_2):
    graph_a = igraph_from_molecule(mol_1)
    graph_b = igraph_from_molecule(mol_2)
    match = graph_a.isomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)
    return match


def filter_for_molecules_not_in_set(molecules, mol_set):
    not_present_molecules = []
    existing_mol_graphs = map(lambda existing_mol: igraph_from_molecule(existing_mol), mol_set)
    for molecule in molecules:
        mol_graph = igraph_from_molecule(molecule)
        if not is_isomorphic_to_any(mol_graph, existing_mol_graphs):
            not_present_molecules.append(molecule)
    return not_present_molecules


def is_isomorphic_to_any(graph, graphs):
    for other_graph in graphs:
        if graph.isomorphic_vf2(other_graph, node_compat_fn=vertices_are_equal):
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
    print(find_ligand_in_mof(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)
