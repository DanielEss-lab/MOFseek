import unittest

from MofIdentifier.DAO import SBUDAO
from MofIdentifier.fileIO import CifReader


class SBUDAOTest(unittest.TestCase):
    def test_add_and_get(self):
        mof = CifReader.get_mof("../mofsForTests/smod7-pos-1.cif")
        sbu = mof.sbus().clusters[0]
        name = SBUDAO.process_sbu(sbu, mof)
        self.assertEqual(1, len(SBUDAO.get_all_names()))
        self.assertEqual('cluster_0', name)

    def test_get_sbu(self):
        sbu = SBUDAO.get_sbu("cluster_0")
        self.assertIsNotNone(sbu)
        print(sbu)


if __name__ == '__main__':
    unittest.main()
