from MofIdentifier.Molecules import atom


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


def match(mol1, mol2):
    if mol1.should_use_weak_comparison or mol2.should_use_weak_comparison:
        return mol_near_isomorphic(mol1, mol2)
    else:
        return mol_are_isomorphic(mol1, mol2)


def find_ligand_in_mof(ligand, mof):
    lGraph = ligand.get_graph()
    if len(lGraph.clusters()) != 1:
        raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input file '
                        'and try again.')
    mGraph = mof.get_graph()
    mof_contains_ligand = mGraph.subisomorphic_vf2(lGraph, node_compat_fn=vertices_are_equal)
    return mof_contains_ligand


def filter_for_mofs_with_ligands(mofs, ligands):
    mofs_containing_ligands = []
    for mof in mofs:
        if mof_has_all_ligands(mof, ligands):
            mofs_containing_ligands.append(mof)
    return mofs_containing_ligands


def mof_has_all_ligands(mof, ligands):
    for ligand in ligands:
        mof_contains_ligand = mof.get_graph().subisomorphic_vf2(ligand.get_graph(), node_compat_fn=vertices_are_equal)
        if not mof_contains_ligand:
            return False
    return True


def name_molecules_from_set(molecules, mol_set):  # Can operate on anything with .atoms and .label (ie sbus, Ligands)
    not_present_molecules = []
    present_molecules = []
    for molecule in molecules:
        if does_assign_label_from_set(molecule, mol_set):
            present_molecules.append(molecule)
        else:
            not_present_molecules.append(molecule)
    return not_present_molecules, present_molecules


def does_assign_label_from_set(molecule, mol_set):
    for mol_from_set in mol_set:
        if molecule.get_graph().isomorphic_vf2(mol_from_set.get_graph(), node_compat_fn=vertices_are_equal):
            molecule.label = mol_from_set.label
            return True
    return False


def mol_are_isomorphic(mol_1, mol_2):
    graph_a = mol_1.get_graph()
    graph_b = mol_2.get_graph()
    match = graph_a.isomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)
    return match


def graphs_are_isomorphic(graph_a, graph_b):
    return graph_a.isomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)


# def get_hydrogenless_graph(mol):
#     graph = mol.get_graph().copy()
#     to_delete_ids = [v.index for v in graph.vs if 'H' == v['element']]
#     graph.delete_vertices(to_delete_ids)
#     return graph


def mol_near_isomorphic(mol_1, mol_2):
    graph_a = mol_1.get_hydrogenless_graph()
    graph_b = mol_2.get_hydrogenless_graph()
    return graphs_near_isomorphic(graph_a, graph_b)


def graphs_near_isomorphic(graph_a, graph_b):
    if graph_a.vcount() != graph_b.vcount():
        return False
    match = (graph_a.subisomorphic_vf2(graph_b, node_compat_fn=vertices_are_equal)
             or graph_b.subisomorphic_vf2(graph_a, node_compat_fn=vertices_are_equal))
    return match
