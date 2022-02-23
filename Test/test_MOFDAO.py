import unittest

from DAOsAndServices import MOFDAO, DBConnection, simpleMOFDAO
from MofIdentifier.fileIO import CifReader


class MOFDAOTest(unittest.TestCase):
    def test_put_and_get(self):
        DBConnection.use_test_connections()
        mof = CifReader.get_mof("../MofIdentifier/mofsForTests/smod7-pos-1.cif")
        MOFDAO.add_mof(mof)
        retrieved_mof = MOFDAO.get_MOF(mof.label)
        self.assertIsNotNone(retrieved_mof)
        self.assertEqual(1, len(retrieved_mof.sbu_nodes))

    def test_get_and_store_value(self):
        DBConnection.use_test_connections()
        mof = CifReader.get_mof("../MofIdentifier/mofsForTests/smod7-pos-1.cif")
        MOFDAO.add_mof(mof)
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertIsNotNone(retrieved_mof)
        unit_volume = retrieved_mof.unit_volume
        simpleMOFDAO.store_value(retrieved_mof.filename, 'unit_volume', -13)
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertEqual(-13, retrieved_mof.unit_volume)
        simpleMOFDAO.store_value(retrieved_mof.filename, 'unit_volume', unit_volume)
        retrieved_mof = MOFDAO.get_MOF('smod7-pos-1.cif')
        self.assertEqual(unit_volume, retrieved_mof.unit_volume)


if __name__ == '__main__':
    unittest.main()
