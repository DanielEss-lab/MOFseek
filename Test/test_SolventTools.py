import unittest

from MofIdentifier.bondTools import SolventTools
from MofIdentifier.fileIO import CifReader


class CountSolventsTest(unittest.TestCase):
    def test_cif_without_solvent(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        self.assertEqual(0, len(mof.solvents))

    def test_cif_with_solvent(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/TUGSOE_charged.cif')
        self.assertEqual(1, len(mof.solvents))

    def test_cif_with_multiple_pieces(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/UGOSOY_charged.cif')
        self.assertEqual(1, len(mof.solvents))


class FileContentWithoutSolventsTest(unittest.TestCase):
    def test_cif_without_solvent(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        self.assertEqual(mof.file_content, SolventTools.get_file_content_without_solvents(mof))

    def test_cif_with_solvent(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/TUGSOE_charged.cif')
        split_file_content = SolventTools.get_file_content_without_solvents(mof).split('\n')
        self.assertEqual(len(mof.file_content.split('\n')) - 32, len(split_file_content))
        self.assertFalse(any(line.startswith('O') for line in split_file_content))

    def test_cif_with_multiple_pieces(self):
        mof = CifReader.get_mof('../MofIdentifier/mofsForTests/UGOSOY_charged.cif')
        split_file_content = SolventTools.get_file_content_without_solvents(mof).split('\n')
        self.assertEqual(len(mof.file_content.split('\n')) - 20, len(split_file_content))
        self.assertFalse(any(line.startswith('Cl') for line in split_file_content))

if __name__ == '__main__':
    unittest.main()
