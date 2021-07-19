import unittest

from GUI.Search.SearchTerms import SearchTerms
from MofIdentifier.fileIO import CifReader, LigandReader


class SearchTermsTest(unittest.TestCase):
    def test_ligands(self):
        mof = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        SO4 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/PO4.xyz')
        M6 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/M6_node.xyz')
        search_SO4_present = SearchTerms([SO4])
        search_M6_present = SearchTerms([M6])
        self.assertTrue(search_SO4_present.passes(mof))
        self.assertFalse(search_M6_present.passes(mof))

    def test_excl_ligands(self):
        mof = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        SO4 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/PO4.xyz')
        M6 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/M6_node.xyz')
        search_SO4_not_present = SearchTerms(excl_ligands=[SO4])
        search_M6_not_present = SearchTerms(excl_ligands=[M6])
        self.assertTrue(search_M6_not_present.passes(mof))
        self.assertFalse(search_SO4_not_present.passes(mof))

    def test_sbus(self):
        mof_with_sbu = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        mof_without_sbu = CifReader.get_mof('../../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        SO4 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/PO4.xyz')
        search_sbu = SearchTerms(sbus=[SO4])
        self.assertTrue(search_sbu.passes(mof_with_sbu))
        self.assertFalse(search_sbu.passes(mof_without_sbu))

    def test_excl_sbus(self):
        mof_with_sbu = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        mof_without_sbu = CifReader.get_mof('../../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        SO4 = LigandReader.get_mol_from_file('../../MofIdentifier/ligands/PO4.xyz')
        search_excl_sbu = SearchTerms(excl_sbus=[SO4])
        self.assertFalse(search_excl_sbu.passes(mof_with_sbu))
        self.assertTrue(search_excl_sbu.passes(mof_without_sbu))

    def test_elem(self):
        mof_with_elem = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        mof_without_elem = CifReader.get_mof('../../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        search = SearchTerms(elements=['P', 'Mo'])
        self.assertTrue(search.passes(mof_with_elem))
        self.assertFalse(search.passes(mof_without_elem))

    def test_excl_elem(self):
        mof_with_elem = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        mof_without_elem = CifReader.get_mof('../../MofIdentifier/mofsForTests/ABAVIJ_clean.cif')
        search_excl = SearchTerms(excl_elements=['P', 'Mo'])
        self.assertFalse(search_excl.passes(mof_with_elem))
        self.assertTrue(search_excl.passes(mof_without_elem))

    def test_label(self):
        mof_with_name = CifReader.get_mof('../../MofIdentifier/mofsForTests/AKOHEO_clean.cif')
        mof_without_name = CifReader.get_mof('../../MofIdentifier/mofsForTests/SOTXEG_neutral.cif')
        search = SearchTerms(label='clean')
        self.assertTrue(search.passes(mof_with_name))
        self.assertFalse(search.passes(mof_without_name))

    def test_numerical_attr(self):
        mof_with_aux = CifReader.get_mof('../../MofIdentifier/mofsForTests/smod7-pos-1.cif')
        mof_without_aux = CifReader.get_mof('../../MofIdentifier/mofsForTests/RUSSAA_clean.cif')
        min_search = SearchTerms(numerical_attr={'Aux/\u212B\u00B3': (10**-4, None)})
        max_search = SearchTerms(numerical_attr={'Aux/\u212B\u00B3': (None, 0)})
        self.assertTrue(min_search.passes(mof_with_aux))
        self.assertFalse(min_search.passes(mof_without_aux))
        self.assertFalse(max_search.passes(mof_with_aux))
        self.assertTrue(max_search.passes(mof_without_aux))


if __name__ == '__main__':
    unittest.main()
