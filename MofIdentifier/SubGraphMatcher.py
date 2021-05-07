import time
from MofIdentifier import XyzReader, CifReader, atom
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator
import igraph


def vertices_are_equal(g1, g2, i1, i2):
    elem_1 = g1.vs[i1]['element']
    elem_2 = g2.vs[i2]['element']
    result = elem_1 == elem_2 \
        or elem_1 == '*' or elem_2 == '*' \
        or (elem_1 == '%' and atom.isMetal(elem_2)) or (elem_2 == '%' and atom.isMetal(elem_1)) \
        or (elem_1 == '#' and (elem_2 == 'H' or elem_2 == 'C')) or (elem_2 == '#' and (elem_1 == 'H' or elem_1 == 'C'))
    return result


def find_ligand_in_mof(ligand, mof):
    # before_setup_time = time.time()
    lGraph = igraph.Graph()
    for atom in ligand.atoms:
        lGraph.add_vertex(atom.label, element=atom.type_symbol)
    for atom in ligand.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
                assert (bonded_atom in ligand.atoms)
            lGraph.add_edge(atom.label, bonded_atom.label)
    if len(lGraph.clusters()) != 1:
        raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input file '
                        'and try again.')
    mGraph = igraph.Graph()
    for atom in mof.atoms:
        mGraph.add_vertex(atom.label, element=atom.type_symbol)
    for atom in mof.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
                assert (bonded_atom in mof.atoms)
            mGraph.add_edge(atom.label, bonded_atom.label)
    # after_setup_time = time.time()
    mof_contains_ligand = mGraph.subisomorphic_vf2(lGraph, node_compat_fn=vertices_are_equal)
    # end_time = time.time()
    # print('time to make graphs: {}'.format(after_setup_time - before_setup_time))
    # print('time to run VF2: {}'.format(end_time - after_setup_time))
    return mof_contains_ligand


if __name__ == '__main__':
    bond_creator = XyzBondCreator()

    ligand = XyzReader.read_xyz('ligandsWildcards/CO2_1.xyz')
    bond_creator.connect_atoms(ligand)
    molecule = XyzReader.read_xyz('ligandsWildcards/contains_CO2_1_bad.xyz')
    bond_creator.connect_atoms(molecule)

    before_read_time = time.time()
    print("Ligand in mof: ")
    print(find_ligand_in_mof(ligand, molecule))
    after_find_time = time.time()
    print('time to find ligand: {}'.format(after_find_time - before_read_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)
