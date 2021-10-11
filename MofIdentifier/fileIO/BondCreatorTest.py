import unittest

from MofIdentifier.bondTools import Distances
from MofIdentifier.fileIO import CifReader


class MyTestCase(unittest.TestCase):
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

    def test_breaking_metals_based_on_borderline_angles(self):
        complex_mof = CifReader.get_mof('../mofsForTests/YOJMAN_clean.cif')
        na1 = None
        k8 = None
        n4 = None
        for atom in complex_mof.atoms:
            if atom.label == 'K8':
                k8 = atom
            if atom.label == 'Na1':
                na1 = atom
            if atom.label == 'N4':
                n4 = atom

        self.assertNotIn(k8, na1.bondedAtoms)
        self.assertNotIn(na1, k8.bondedAtoms)
        self.assertIn(na1, n4.bondedAtoms)
        self.assertIn(k8, n4.bondedAtoms)

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


if __name__ == '__main__':
    unittest.main()
