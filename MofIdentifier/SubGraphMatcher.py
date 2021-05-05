import time
from MofIdentifier import XyzReader, CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator
import igraph


def vertices_are_equal(g1, g2, i1, i2):
    elem_1 = g1.vs[i1]['element']
    elem_2 = g2.vs[i2]['element']
    return elem_1 == elem_2 or elem_1 == '*' or elem_2 == '*' or elem_1 == '%' or elem_2 == '%'


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
    benzene = XyzReader.read_xyz('BenzeneWildCard.xyz')
    bond_creator.connect_atoms(benzene)
    not_benzene = XyzReader.read_xyz('NotBenzeneWildCard.xyz')
    bond_creator.connect_atoms(not_benzene)
    mof_808 = CifReader.read_mof('smod7-pos-1.cif')
    bond_creator = MofBondCreator(mof_808)
    bond_creator.connect_atoms()

    before_read_time = time.time()
    print("Benzene in mof: (expected True)")
    print(find_ligand_in_mof(benzene, mof_808))

    after_find_time = time.time()
    print("Messed up Benzene in mof: (expected False)")
    print(find_ligand_in_mof(not_benzene, mof_808))
    after_miss_time = time.time()
    print('time to find benzene: {}'.format(after_find_time - before_read_time))
    print('time to declare does not contain benzene-with-Hydrgoen: {}'.format(after_miss_time - after_find_time))
    # Note that most of that time goes into creating the graphs, not running the algorithm (for now)
