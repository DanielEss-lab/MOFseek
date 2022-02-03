import unittest

from MofIdentifier.bondTools import OpenMetalSites
from MofIdentifier.fileIO import CifReader


class MyTestCase(unittest.TestCase):
    def test_close_double_metal_inner_sites(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/ABAYIO_clean.cif')
        self.assertEqual(0, len(mof.open_metal_sites))

    def test_far_double_metal_inner_sites(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/AFITUF_clean.cif')
        self.assertEqual(0, len(mof.open_metal_sites))

    def test_metal_with_five_bonds(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/ac403674p_si_001_clean.cif')
        self.assertEqual(6, len(mof.open_metal_sites))

    def test_metal_with_many_bonds(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/LOQSOA_clean.cif')
        self.assertEqual(0, len(mof.open_metal_sites))

    def test_filling_one_side_of_square_planar(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/AGUTUS_clean.cif')
        self.assertTrue([atom for atom in mof.atoms if atom.label == 'Cu1'][0].open_metal_site)
        self.assertEqual(5, len([atom for atom in mof.atoms if atom.label == 'Cu1'][0].bondedAtoms))

    def test_center_by_weight_when_all_equal_weight(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/ACAKUM_clean.cif')
        self.assertEqual(4, len(mof.open_metal_sites))

    def test_no_OMS_if_center_is_center(self):
        mof = CifReader.get_mof(r'../MofIdentifier/mofsForTests/acs.inorgchem.6b00894_ic6b00894_si_003_clean.cif')
        self.assertEqual(0, len(mof.open_metal_sites))

    def test_estimate_by_geom_when_geom_center_farther_than_mass_center(self):
        name = 'FAZPED_clean'
        mof = CifReader.get_mof(fr'../mofsForTests/{name}.cif')
        self.assertEqual(6, len(mof.open_metal_sites))

    def test_estimate_by_geom_when_geom_center_farther_than_mass_center(self):
        name = 'RANPAA_clean'
        mof = CifReader.get_mof(fr'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\{name}.cif')
        self.assertEqual(2, len(mof.open_metal_sites))


if __name__ == '__main__':
    unittest.main()
