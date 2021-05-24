from MofIdentifier import atom
from MofIdentifier.SubGraphMatching import WeakSubGraphMatcher, StrongSubGraphMatcher


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


def graph_from_mol(mol1):
    if mol1.should_use_weak_comparison:
        graph1 = WeakSubGraphMatcher.igraph_from_molecule(mol1)
    else:
        graph1 = StrongSubGraphMatcher.igraph_from_molecule(mol1)
    return graph1


def match(mol1, mol2):
    if mol1.should_use_weak_comparison or mol2.should_use_weak_comparison:
        return WeakSubGraphMatcher.mol_near_isomorphic(mol1, mol2)
    else:
        return StrongSubGraphMatcher.mol_are_isomorphic(mol1, mol2)


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
