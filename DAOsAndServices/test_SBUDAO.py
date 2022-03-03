import unittest

from DAOsAndServices import SBUDAO, DBConnection, MOFDAO
from GUI.Pages.Search.SearchTerms import SearchTerms
from MofIdentifier.fileIO import CifReader


class SBUDAOTest(unittest.TestCase):
    def test_add_and_get(self):
        DBConnection.use_test_connections()
        # SBUDAO.delete_all_sbus()  # this WILL actually delete everything, so don't uncomment this unless you need to
        mof = CifReader.get_mof("../MofIdentifier/mofsForTests/smod7-pos-1.cif")
        sbu = mof.sbus().clusters[0]
        name = SBUDAO.process_sbu(sbu, 'smod7-pos-1')
        self.assertEqual(1, len(SBUDAO.get_all_names()))
        self.assertEqual('cluster_0', name)

    def test_get_sbu(self):
        DBConnection.use_test_connections()
        sbu = SBUDAO.get_sbu("cluster_0")
        self.assertIsNotNone(sbu)
        print(sbu)

    def test_search_sbu(self):
        sbu = SBUDAO.get_sbu("auxiliary_2")
        search = SearchTerms(sbus=[sbu.name])
        # mof1 = MOFDAO.get_MOF("acscombsci.5b00188_3001288_clean")
        mof2 = MOFDAO.get_MOF("ac403674p_si_001_clean")
        mof1 = MOFDAO.get_MOF("ACOGAB_clean")
        self.assertTrue(search.passes(mof2))
        self.assertTrue(search.passes(mof1))


if __name__ == '__main__':
    unittest.main()
