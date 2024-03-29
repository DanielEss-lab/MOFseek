from MofIdentifier.Molecules import Atom
import time


# def vertices_are_equal(g1, g2, i1, i2):
#     elem_1 = g1.vs[i1]['element']
#     elem_1 = elem_1[0] if len(elem_1) > 1 and elem_1[1].isnumeric() else elem_1
#     elem_2 = g2.vs[i2]['element']
#     elem_2 = elem_2[0] if len(elem_2) > 1 and elem_2[1].isnumeric() else elem_2
#     result = elem_1 == elem_2 \
#              or elem_1 == '*' or elem_2 == '*' \
#              or (elem_1 == '&' and atom.is_metal(elem_2)) or (elem_2 == '&' and atom.is_metal(elem_1)) \
#              or (elem_1 == '~' and (elem_2 == 'H' or elem_2 == 'C')) or (
#                      elem_2 == '~' and (elem_1 == 'H' or elem_1 == 'C'))
#     return result
def elements_are_compatible(elem_1, elem_2, additional_wildcards):
    return elem_1 == elem_2 \
           or elem_1 == '*' or elem_2 == '*' \
           or (elem_1 == '&' and Atom.is_metal(elem_2)) or (elem_2 == '&' and Atom.is_metal(elem_1)) \
           or (elem_1 == '~' and (elem_2 == 'H' or elem_2 == 'C')) \
           or (elem_2 == '~' and (elem_1 == 'H' or elem_1 == 'C')) \
           or (elem_1 in additional_wildcards and additional_wildcards[elem_1].matches(elem_2)) \
           or (elem_2 in additional_wildcards and additional_wildcards[elem_2].matches(elem_1))


def timed_vertices_are_equal(start, additional_wildcards):
    if additional_wildcards is None:
        additional_wildcards = []

    def vertices_are_equal(g1, g2, i1, i2):
        if start != 0 and time.time() - start > 40:
            print('VF2 Algorithm got stuck (somehow); exiting early')
            return False
        if g2.vs[i2]['is_bond_limited']:
            if len(g1.neighbors(i1)) != len(g2.neighbors(i2)):
                return False
        elem_1 = g1.vs[i1]['element']
        elem_1 = elem_1[0] if len(elem_1) > 1 and elem_1[-1].isnumeric() else elem_1
        elem_2 = g2.vs[i2]['element']
        elem_2 = elem_2[0] if len(elem_2) > 1 and elem_2[-1].isnumeric() else elem_2
        return elements_are_compatible(elem_1, elem_2, additional_wildcards)

    return vertices_are_equal


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
    if not all(element_in_mof(element, mof) for element in ligand.concrete_elements_present()):
        return False
    start = time.time()
    mof_contains_ligand = \
        mGraph.subisomorphic_vf2(lGraph, node_compat_fn=timed_vertices_are_equal(start, ligand.unique_wildcards))
    return mof_contains_ligand


def element_in_mof(element, mof):
    if element[0] == '*':
        return True
    elif element[0] == '~':
        return any(elem == 'H' or elem == 'C' for elem in mof.elementsPresent)
    elif element[0] == '&':
        return any(Atom.is_metal(elem) for elem in mof.elementsPresent)
    else:
        return element in mof.elementsPresent


def mof_has_all_ligands(mof, ligands):
    for ligand in ligands:
        if not find_ligand_in_mof(ligand, mof):
            return False
    return True


def mof_has_no_ligands(mof, ligands):
    for ligand in ligands:
        if find_ligand_in_mof(ligand, mof):
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
        if match(molecule, mol_from_set):
            molecule.graph = mol_from_set.graph  # We give it the set molecule's graph as well, in case the set had a
            molecule.no_h_graph = mol_from_set.no_h_graph  # more general graph using wildcards
            molecule.label = mol_from_set.label
            molecule.filepath = mol_from_set.filepath
            molecule.file_content = mol_from_set.file_content
            return True
    return False


def mol_are_isomorphic(mol_1, mol_2):
    graph_a = mol_1.get_graph()
    graph_b = mol_2.get_graph()
    additional_wildcards = mol_1.unique_wildcards if mol_1.unique_wildcards is not None else mol_2.unique_wildcards
    match = graph_a.isomorphic_vf2(graph_b, node_compat_fn=timed_vertices_are_equal(time.time(), additional_wildcards))
    return match


def mapping_function(mol_1, mol_2):
    graph_a = mol_1.get_graph()
    graph_b = mol_2.get_graph()
    (is_match, mapping_12, _) = graph_a.isomorphic_vf2(graph_b,
                                                       node_compat_fn=timed_vertices_are_equal(time.time(), list()),
                                                       return_mapping_12=True)

    def mol2atomlabel_from_mol1atomlabel(atom_label):
        a_vertex = graph_a.vs.find(atom_label)
        match_index = mapping_12[a_vertex.index]
        b_vertex = graph_b.vs.find(match_index)
        return b_vertex['name']

    return is_match, mol2atomlabel_from_mol1atomlabel


def vertices_near_equal(g1, g2, i1, i2):
    elem_1 = g1.vs[i1]['element']
    elem_1 = elem_1[0] if len(elem_1) > 1 and elem_1[-1].isnumeric() else elem_1
    elem_2 = g2.vs[i2]['element']
    elem_2 = elem_2[0] if len(elem_2) > 1 and elem_2[-1].isnumeric() else elem_2
    return elements_are_compatible(elem_1, elem_2, [])


def mol_near_isomorphic(mol_1, mol_2):
    graph_a = mol_1.get_hydrogenless_graph()
    graph_b = mol_2.get_hydrogenless_graph()
    if graph_a.vcount() != graph_b.vcount():
        return False
    match = (graph_a.subisomorphic_vf2(graph_b, node_compat_fn=vertices_near_equal)
             or graph_b.subisomorphic_vf2(graph_a, node_compat_fn=vertices_near_equal))
    return match
