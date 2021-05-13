import unittest

from MofIdentifier import XyzReader, CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.SubGraphMatcher import find_ligand_in_mof
from MofIdentifier.XyzBondCreator import XyzBondCreator


class SubGraphMatcherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bond_creator = XyzBondCreator()
        cls.mof_808 = CifReader.read_mof('mofsForTests/smod7-pos-1.cif')
        bond_creator = MofBondCreator(cls.mof_808)
        bond_creator.connect_atoms()

    def test_single_atom(self):
        carbon = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/SingleCarbon.xyz'))
        iron = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/SingleIron.xyz'))
        self.assertEqual(True, find_ligand_in_mof(carbon, carbon), "Carbon should be subgraph of Carbon")
        self.assertEqual(True, find_ligand_in_mof(iron, iron), "Iron should be subgraph of Iron")
        self.assertEqual(False, find_ligand_in_mof(carbon, iron), "Carbon should not be subgraph of Iron")
        self.assertEqual(False, find_ligand_in_mof(iron, carbon), "Iron should not be subgraph of Carbon")

    def test_atom_in_ligand(self):
        carbon = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/SingleCarbon.xyz'))
        iron = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/SingleIron.xyz'))
        benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/BenzeneBase.xyz'))
        self.assertEqual(True, find_ligand_in_mof(carbon, benzene), "Carbon should be subgraph of Benzene")
        self.assertEqual(False, find_ligand_in_mof(iron, benzene), "Iron should not be subgraph of Benzene")

    def test_ligand_in_ligand(self):
        benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/BenzeneBase.xyz'))
        solitary_benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/Benzene.xyz'))
        self.assertEqual(True, find_ligand_in_mof(benzene, solitary_benzene), "Benzene(6C) should be "
                                                                              "subgraph of Benzene(6C, 6H")
        self.assertEqual(False, find_ligand_in_mof(solitary_benzene, benzene), "Not other way around")

    def test_ligand_in_mof(self):
        benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/BenzeneBase.xyz'))
        solitary_benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/Benzene.xyz'))
        self.assertEqual(True, find_ligand_in_mof(benzene, self.mof_808), "Benzene(6C) should be in mof")
        self.assertEqual(False, find_ligand_in_mof(solitary_benzene, self.mof_808), "Filled Benzene(6C, 6H) "
                                                                                    "should not be in mof")

    def test_requires_single_ligand(self):
        benzene = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/BenzeneBase.xyz'))
        six_carbon = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligands/six_disjoint_carbons.xyz'))
        with self.assertRaises(Exception):
            find_ligand_in_mof(six_carbon, benzene)

    def test_asterisk_WCA(self):
        # To match anything
        H2O_1 = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/H2O_1.xyz'))
        H2O_2 = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/H2O_2.xyz'))
        H20_good_ex = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/H2O_1_good.xyz'))
        H20_bad_ex = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/H2O_1_bad.xyz'))
        self.assertEqual(True, find_ligand_in_mof(H2O_1, H20_good_ex), "Should find match in structures")
        self.assertEqual(True, find_ligand_in_mof(H2O_2, H20_good_ex), "Should find match in structures")
        self.assertEqual(False, find_ligand_in_mof(H2O_1, H20_bad_ex), "Should not find match in structures")
        self.assertEqual(False, find_ligand_in_mof(H2O_2, H20_bad_ex), "Should not find match in structures")

    def test_percent_sign_WCA(self):
        # To match metals only
        m6 = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/M6_node.xyz'))
        m6_fe = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/M6_node_compact.xyz'))
        m6_bad = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/contains_M6_node_bad.xyz'))
        self.assertEqual(True, find_ligand_in_mof(m6, m6_fe), "Should find match in structures")
        self.assertEqual(False, find_ligand_in_mof(m6, m6_bad), "Should not find match in structures")

    def test_pound_sign_WCA(self):
        # To match Carbon and Hydrogen only
        CO2_1 = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/CO2_1.xyz'))
        CO2_1_good_ex = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/contains_CO2_1_good.xyz'))
        CO2_1_bad_ex = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/contains_CO2_1_bad.xyz'))
        self.assertEqual(True, find_ligand_in_mof(CO2_1, CO2_1_good_ex), "Should find match in structures")
        self.assertEqual(False, find_ligand_in_mof(CO2_1, CO2_1_bad_ex), "Should not find match in structures")

    def test_numbered_bond_WCA(self):
        m6 = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/M6_node_alternate.xyz'))
        m6_fe = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/M6_node_compact.xyz'))
        m6_bad = self.bond_creator.connect_atoms(XyzReader.read_xyz('ligandsWildcards/contains_M6_node_bad.xyz'))
        self.assertEqual(True, find_ligand_in_mof(m6, m6_fe), "Should find match in structures")
        self.assertEqual(False, find_ligand_in_mof(m6, m6_bad), "Should not find match in structures")


if __name__ == '__main__':
    unittest.main()
