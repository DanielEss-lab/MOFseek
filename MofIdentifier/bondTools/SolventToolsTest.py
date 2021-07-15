import unittest

from MofIdentifier.fileIO import CifReader


class SolventToolsTest(unittest.TestCase):
    def test_cif_without_solvent(self):
        mof = CifReader.get_mof('../mofsForTests/ABAVIJ_clean.cif')
        self.assertEqual(0, len(mof.solvents))

    def test_cif_with_solvent(self):
        mof = CifReader.get_mof('../mofsForTests/TUGSOE_charged.cif')
        self.assertEqual(1, len(mof.solvents))

    def test_cif_with_multiple_pieces(self):
        mof = CifReader.get_mof('../mofsForTests/UGOSOY_charged.cif')
        self.assertEqual(1, len(mof.solvents))


if __name__ == '__main__':
    unittest.main()
