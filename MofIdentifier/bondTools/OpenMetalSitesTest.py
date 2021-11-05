import unittest

from MofIdentifier.bondTools import OpenMetalSites
from MofIdentifier.fileIO import CifReader


class MyTestCase(unittest.TestCase):
    def test_double_metal_inner_sites(self):
        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\ABAYIO_clean.cif")
        atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance = OpenMetalSites.process(mof, True)
        self.assertIsNotNone(example_atom)

        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\AFITUF_clean.cif")
        atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance = OpenMetalSites.process(mof, True)
        self.assertIsNotNone(example_atom)


if __name__ == '__main__':
    unittest.main()
