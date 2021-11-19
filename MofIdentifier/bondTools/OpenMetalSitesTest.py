import unittest

from MofIdentifier.bondTools import OpenMetalSites
from MofIdentifier.fileIO import CifReader


class MyTestCase(unittest.TestCase):
    def test_double_metal_inner_sites(self):
        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\ABAYIO_clean.cif")
        self.assertGreater(len(mof.open_metal_sites), 0)

        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\AFITUF_clean.cif")
        self.assertGreater(len(mof.open_metal_sites), 0)

    def test_metal_with_many_bonds(self):
        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\ac403674p_si_001_clean.cif")
        self.assertEqual(len(mof.open_metal_sites), 0)

    def test_metal_with_collapsing_bonds(self):
        mof = CifReader.get_mof(
            r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\LOQSOA_clean.cif")
        self.assertEqual(len(mof.open_metal_sites), 0)


if __name__ == '__main__':
    unittest.main()
