import os
import unittest

from MetalModifier.main import *
from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


def count_node_protons(mof):
    clusters = SBUIdentifier.split(mof, True).nodes_with_auxiliaries()
    clusters = [cluster for cluster in clusters if len(cluster[0].atoms) > 1]
    assert (len(clusters) > 0)
    assert (all(cluster[0] == clusters[0][0] for cluster in clusters))
    num_protons = count_added_protons(clusters[0])
    return num_protons


class WriteAtomTest(unittest.TestCase):
    def test_cartesian_to_fractional(self):
        replace_metal(r'../MofIdentifier/mofsForTests/smod7-pos-1.cif',
                      r'TestResources/smod7-except-Y.cif', 'Y')
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/smod7-pos-1.cif')
        original_atom = mof.atoms[0]
        fractional_atom = Atom.from_fractional(original_atom.label, original_atom.type_symbol, original_atom.a,
                                               original_atom.b, original_atom.c, mof.angles, mof.fractional_lengths)
        cartesian_atom = Atom.from_cartesian(original_atom.label, original_atom.type_symbol, original_atom.x,
                                             original_atom.y, original_atom.z, mof)
        self.assertAlmostEqual(original_atom.x, fractional_atom.x)
        self.assertAlmostEqual(original_atom.x, cartesian_atom.x)
        self.assertAlmostEqual(original_atom.a, fractional_atom.a)
        self.assertAlmostEqual(original_atom.a, cartesian_atom.a)


class ChangeMetalTest(unittest.TestCase):
    def test_Zr_to_Y(self):
        replace_metal(r'../MofIdentifier/mofsForTests/smod7-pos-1.cif',
                      r'TestResources/smod7-except-Y.cif', 'Y')
        new_mof = CifReader.get_mof(r'TestResources/smod7-except-Y.cif')
        self.assertTrue('Y' in new_mof.atoms_string())
        self.assertEqual(protons_needed('Y'), count_node_protons(new_mof))

    def test_Zr_to_V(self):
        replace_metal(r'../MofIdentifier/mofsForTests/smod7-pos-1.cif',
                      r'TestResources/smod7-except-V.cif', 'V')
        new_mof = CifReader.get_mof(r'TestResources/smod7-except-V.cif')
        self.assertTrue('V' in new_mof.atoms_string())
        self.assertEqual(protons_needed('V'), count_node_protons(new_mof))

    def test_add_group_0(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-0-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_group_0_atoms(cluster).add_atoms  # Add'ems, hahahaha
        self.assertEqual(8, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-0-h.cif',
                      r'TestResources/smod7-one-node-temp-8.cif', '8')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-8.cif')
        self.assertEqual(8, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-8.cif')

    def test_add_group_1(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-8-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_group_1_atoms(cluster, mof).add_atoms
        self.assertEqual(4, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-8-h.cif',
                      r'TestResources/smod7-one-node-temp-12.cif', '12')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-12.cif')
        self.assertEqual(12, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-12.cif')

    def test_add_group_2(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-12-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_groups_2_and_3_atoms(cluster).add_atoms
        self.assertEqual(8, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-12-h.cif',
                      r'TestResources/smod7-one-node-temp-16.cif', '16')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-16.cif')
        self.assertEqual(16, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-16.cif')

    def test_add_group_3(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-16-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_groups_2_and_3_atoms(cluster).add_atoms
        self.assertEqual(4, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-16-h.cif',
                      r'TestResources/smod7-one-node-temp-20.cif', '20')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-20.cif')
        self.assertEqual(20, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-20.cif')

    def test_add_group_4(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-20-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_group_4_atoms(cluster).add_atoms
        self.assertEqual(2, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-20-h.cif',
                      r'TestResources/smod7-one-node-temp-22.cif', '22')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-22.cif')
        self.assertEqual(22, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-22.cif')

    def test_add_group_5(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-22-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        add_atoms = get_relevant_group_5_atoms(cluster, mof).add_atoms
        self.assertEqual(4, len(add_atoms))
        replace_metal(r'TestResources/smod7-one-node-22-h.cif',
                      r'TestResources/smod7-one-node-temp-26.cif', '26')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-26.cif')
        self.assertEqual(26, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-26.cif')

    def test_delete_group_5(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-26-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_group_5_atoms(cluster, mof).delete_atoms
        self.assertEqual(4, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-26-h.cif',
                      r'TestResources/smod7-one-node-temp-22-d.cif', '22')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-22-d.cif')
        self.assertEqual(22, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-22-d.cif')

    def test_delete_group_4(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-22-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_group_4_atoms(cluster).delete_atoms
        self.assertEqual(2, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-22-h.cif',
                      r'TestResources/smod7-one-node-temp-20-d.cif', '20')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-20-d.cif')
        self.assertEqual(20, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-20-d.cif')

    def test_delete_group_3(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-20-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_groups_2_and_3_atoms(cluster).delete_atoms
        self.assertEqual(8, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-20-h.cif',
                      r'TestResources/smod7-one-node-temp-16-d.cif', '16')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-16-d.cif')
        self.assertEqual(16, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-16-d.cif')

    def test_delete_group_2(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-16-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_groups_2_and_3_atoms(cluster).delete_atoms
        self.assertEqual(4, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-16-h.cif',
                      r'TestResources/smod7-one-node-temp-12-d.cif', '12')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-12-d.cif')
        self.assertEqual(12, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-12-d.cif')

    def test_delete_group_1(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-12-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_group_1_atoms(cluster, mof).delete_atoms
        self.assertEqual(4, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-12-h.cif',
                      r'TestResources/smod7-one-node-temp-8-d.cif', '8')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-8-d.cif')
        self.assertEqual(8, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-8-d.cif')

    def test_delete_group_0(self):
        mof = CifReader.get_mof(r'TestResources/smod7-one-node-8-h.cif')
        cluster = list(SBUIdentifier.split(mof, True).nodes_with_auxiliaries())[0]
        delete_atoms = get_relevant_group_0_atoms(cluster).delete_atoms
        self.assertEqual(8, len(delete_atoms))
        replace_metal(r'TestResources/smod7-one-node-8-h.cif',
                      r'TestResources/smod7-one-node-temp-0-d.cif', '0')
        new_mof = CifReader.get_mof(r'TestResources/smod7-one-node-temp-0-d.cif')
        self.assertEqual(0, count_node_protons(new_mof))
        os.remove(r'TestResources/smod7-one-node-temp-0-d.cif')



if __name__ == '__main__':
    unittest.main()
