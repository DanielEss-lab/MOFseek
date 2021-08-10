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

    def test_get_and_store_value(self):
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertIsNotNone(retrieved_mof)
        unit_volume = retrieved_mof.unit_volume
        MOFDAO.store_value(retrieved_mof.filename, 'unit_volume', -13)
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertEqual(-13, retrieved_mof.unit_volume)
        MOFDAO.store_value(retrieved_mof.filename, 'unit_volume', unit_volume)
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertEqual(unit_volume, retrieved_mof.unit_volume)


if __name__ == '__main__':
    unittest.main()
