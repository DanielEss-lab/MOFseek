import unittest

from MofIdentifier.DAO import MOFDAO
from MofIdentifier.fileIO import CifReader


class MOFDAOTest(unittest.TestCase):
    def test_put_and_get(self):
        mof = CifReader.get_mof("../mofsForTests/smod7-pos-1.cif")
        MOFDAO.add_mof(mof)
        retrieved_mof = MOFDAO.get_MOF(mof.label)
        self.assertIsNotNone(retrieved_mof)
        self.assertEqual(1, len(retrieved_mof.sbu_nodes))


if __name__ == '__main__':
    unittest.main()
