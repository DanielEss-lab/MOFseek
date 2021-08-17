import unittest
import time

from DAO import MOFDAO
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader


class MyTestCase(unittest.TestCase):
    def test_possible_infinite_loop(self):
        ligand = XyzReader.get_molecule('../MofIdentifier/ligands/L23_no_S.xyz')
        assert(ligand is not None)
        mof = MOFDAO.get_MOF('LIQCUK_clean.cif')
        assert (mof is not None)
        start = time.time()
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(ligand, mof.get_mof()))
        end = time.time()
        self.assertLess(end - start, 20)


if __name__ == '__main__':
    unittest.main()
