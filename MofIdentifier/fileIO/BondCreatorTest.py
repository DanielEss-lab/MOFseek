import unittest

from MofIdentifier.bondTools import Distances
from MofIdentifier.fileIO import CifReader


class MyTestCase(unittest.TestCase):
    def test_fill_nearly_closed_metal_sites(self):
        complex_mof = CifReader.get_mof('../mofsForTests/ABEXEN_clean.cif')
        In1 = None
        for atom in complex_mof.atoms:
            if atom.label == 'In1':
                In1 = atom

        self.assertEqual(8, len(In1.bondedAtoms))

    def test_breaking_metals_based_on_obvious_angles(self):
        complex_mof = CifReader.get_mof('../mofsForTests/YOJMAN_clean.cif')
        k4 = None
        w21 = None
        o65 = None
        for atom in complex_mof.atoms:
            if atom.label == 'K4':
                k4 = atom
            if atom.label == 'W21':
                w21 = atom
            if atom.label == 'O65':
                o65 = atom

        self.assertNotIn(k4, w21.bondedAtoms)
        self.assertNotIn(w21, k4.bondedAtoms)
        self.assertIn(w21, o65.bondedAtoms)
        self.assertIn(k4, o65.bondedAtoms)

    def test_breaking_nonmetal_bonds(self):
        mof = CifReader.get_mof('../mofsForTests/LOQSOA_clean.cif')
        tb1 = None
        n6 = None
        o12 = None
        o13 = None
        for atom in mof.atoms:
            if atom.label == 'Tb1':
                tb1 = atom
            if atom.label == 'N6':
                n6 = atom
            if atom.label == 'O12':
                o12 = atom
            if atom.label == 'O13':
                o13 = atom

        self.assertNotIn(tb1, n6.bondedAtoms)
        self.assertNotIn(n6, tb1.bondedAtoms)
        self.assertIn(n6, o12.bondedAtoms)
        self.assertIn(tb1, o12.bondedAtoms)
        self.assertIn(n6, o13.bondedAtoms)
        self.assertIn(tb1, o13.bondedAtoms)

    def test_arccos(self):
        mof = CifReader.get_mof(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\AKUHOD01_clean.cif')
        Gd2 = None
        Gd4 = None
        O11 = None
        for atom in mof.atoms:
            if atom.label == 'Gd2':
                Gd2 = atom
            if atom.label == 'Gd4':
                Gd4 = atom
            if atom.label == 'O11':
                O11 = atom
        dist_a = Distances.distance_across_unit_cells(Gd2, O11, mof.angles, mof.fractional_lengths)
        dist_b = Distances.distance_across_unit_cells(Gd4, O11, mof.angles, mof.fractional_lengths)
        dist_c = Distances.distance_across_unit_cells(Gd2, Gd4, mof.angles, mof.fractional_lengths)
        self.assertLess(dist_c, dist_a + dist_b)

    def test_OCO_consistent_bonding(self):
        mof = CifReader.get_mof(r'../mofsForTests/acs.inorgchem.6b00894_ic6b00894_si_003_clean.cif')
        num_cd = 0
        for atom in mof.atoms:
            if atom.type_symbol == 'Cd':
                num_cd += 1
                self.assertEqual(6, len(atom.bondedAtoms))
        self.assertEqual(12, num_cd)

    def test_hydrogen_only_one_bond(self):
        mof = CifReader.get_mof(r'../mofsForTests/AWASOI_clean.cif')
        num_h = 0
        for atom in mof.atoms:
            if atom.type_symbol == 'H':
                num_h += 1
                self.assertEqual(1, len(atom.bondedAtoms))
        self.assertEqual(144, num_h)

        mof = CifReader.get_mof(r'../mofsForTests/TEWGEJ01_clean.cif')
        num_h = 0
        for atom in mof.atoms:
            if atom.type_symbol == 'H':
                num_h += 1
                self.assertEqual(1, len(atom.bondedAtoms))
        self.assertEqual(104, num_h)


if __name__ == '__main__':
    unittest.main()
