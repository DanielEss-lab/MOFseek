import unittest

from MofIdentifier.fileIO import XyzReader, CifReader
from MofIdentifier import SubGraphMatcher, WeakSubGraphMatcher


class FindLigandInMofTest(unittest.TestCase):

    def test_single_atom(self):
        carbon = XyzReader.get_molecule('ligands/SingleCarbon.xyz')
        iron = XyzReader.get_molecule('ligands/SingleIron.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(carbon, carbon), "Carbon should be subgraph of Carbon")
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(iron, iron), "Iron should be subgraph of Iron")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(carbon, iron), "Carbon should not be subgraph of Iron")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(iron, carbon), "Iron should not be subgraph of Carbon")

    def test_atom_in_ligand(self):
        carbon = XyzReader.get_molecule('ligands/SingleCarbon.xyz')
        iron = XyzReader.get_molecule('ligands/SingleIron.xyz')
        benzene = XyzReader.get_molecule('ligands/BenzeneBase.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(carbon, benzene), "Carbon should be subgraph of Benzene")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(iron, benzene), "Iron should not be subgraph of Benzene")

    def test_ligand_in_ligand(self):
        benzene = XyzReader.get_molecule('ligands/BenzeneBase.xyz')
        solitary_benzene = XyzReader.get_molecule('ligands/Benzene.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(benzene, solitary_benzene), "Benzene(6C) should be "
                                                                              "subgraph of Benzene(6C, 6H")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(solitary_benzene, benzene), "Not other way around")

    def test_ligand_in_mof(self):
        benzene = XyzReader.get_molecule('ligands/BenzeneBase.xyz')
        solitary_benzene = XyzReader.get_molecule('ligands/Benzene.xyz')
        mof_808 = CifReader.get_mof('mofsForTests/smod7-pos-1.cif')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(benzene, mof_808), "Benzene(6C) should be in mof")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(solitary_benzene, mof_808), "Filled Benzene(6C, 6H) "
                                                                               "should not be in mof")

    def test_requires_single_ligand(self):
        benzene = XyzReader.get_molecule('ligands/BenzeneBase.xyz')
        six_carbon = XyzReader.get_molecule('ligands/six_disjoint_carbons.xyz')
        with self.assertRaises(Exception):
            SubGraphMatcher.find_ligand_in_mof(six_carbon, benzene)

    def test_asterisk_WCA(self):
        # To match anything
        H2O_1 = XyzReader.get_molecule('ligandsWildcards/H2O_1.xyz')
        H2O_2 = XyzReader.get_molecule('ligandsWildcards/H2O_2.xyz')
        H20_good_ex = XyzReader.get_molecule('ligandsWildcards/H2O_1_good.xyz')
        H20_bad_ex = XyzReader.get_molecule('ligandsWildcards/H2O_1_bad.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(H2O_1, H20_good_ex), "Should find match in structures")
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(H2O_2, H20_good_ex), "Should find match in structures")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(H2O_1, H20_bad_ex), "Should not find match in structures")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(H2O_2, H20_bad_ex), "Should not find match in structures")

    def test_percent_sign_WCA(self):
        # To match metals only
        m6 = XyzReader.get_molecule('ligandsWildcards/M6_node.xyz')
        m6_fe = XyzReader.get_molecule('ligandsWildcards/M6_node_compact.xyz')
        m6_bad = XyzReader.get_molecule('ligandsWildcards/contains_M6_node_bad.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(m6, m6_fe), "Should find match in structures")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(m6, m6_bad), "Should not find match in structures")

    def test_pound_sign_WCA(self):
        # To match Carbon and Hydrogen only
        CO2_1 = XyzReader.get_molecule('ligandsWildcards/CO2_1.xyz')
        CO2_1_good_ex = XyzReader.get_molecule('ligandsWildcards/contains_CO2_1_good.xyz')
        CO2_1_bad_ex = XyzReader.get_molecule('ligandsWildcards/contains_CO2_1_bad.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(CO2_1, CO2_1_good_ex), "Should find match in structures")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(CO2_1, CO2_1_bad_ex), "Should not find match in structures")

    def test_numbered_bond_WCA(self):
        m6 = XyzReader.get_molecule('ligandsWildcards/M6_node_alternate.xyz')
        m6_fe = XyzReader.get_molecule('ligandsWildcards/M6_node_compact.xyz')
        m6_bad = XyzReader.get_molecule('ligandsWildcards/contains_M6_node_bad.xyz')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(m6, m6_fe), "Should find match in structures")
        self.assertEqual(False, SubGraphMatcher.find_ligand_in_mof(m6, m6_bad), "Should not find match in structures")

    def test_M6_node_in_various(self):
        m6 = XyzReader.get_molecule('ligandsWildcards/M6_node_alternate.xyz')
        ja500330a_si_006_auto = CifReader.get_mof('mofsForTests/ja500330a_si_006_auto.cif')
        ja500330a_si_007_auto = CifReader.get_mof('mofsForTests/ja500330a_si_007_auto.cif')
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(m6, ja500330a_si_006_auto), "Should find match in structures")
        self.assertEqual(True, SubGraphMatcher.find_ligand_in_mof(m6, ja500330a_si_007_auto), "Should find match in structures")


class WeakSubGraphMatcherTest(unittest.TestCase):

    def test_requiring_all_bonds(self):
        all_bonds_present = XyzReader.get_molecule('ligands/Periodic_55_conn_all_bonds.xyz')
        most_bonds_present = XyzReader.get_molecule('ligands/Periodic_55_conn_some_bonds.xyz')
        self.assertEqual(True, WeakSubGraphMatcher.mol_near_isomorphic(all_bonds_present, most_bonds_present), "Should find match in structures")
        self.assertEqual(False, SubGraphMatcher.are_isomorphic(all_bonds_present, most_bonds_present), "Should not find match in structures")


if __name__ == '__main__':
    unittest.main()
