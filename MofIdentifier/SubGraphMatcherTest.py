import unittest

from MofIdentifier import XyzReader, CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.SubGraphMatcher import find_ligand_in_mof
from MofIdentifier.XyzBondCreator import XyzBondCreator


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carbon = XyzReader.read_xyz('SingleCarbon.xyz')
        bond_creator = XyzBondCreator()
        bond_creator.connect_atoms(cls.carbon)
        cls.iron = XyzReader.read_xyz('SingleIron.xyz')
        bond_creator.connect_atoms(cls.iron)
        cls.benzene = XyzReader.read_xyz('BenzeneBase.xyz')
        bond_creator.connect_atoms(cls.benzene)
        cls.solitary_benzene = XyzReader.read_xyz('Benzene.xyz')
        bond_creator.connect_atoms(cls.solitary_benzene)
        cls.mof_808 = CifReader.read_mof('smod7-pos-1.cif')
        bond_creator = MofBondCreator(cls.mof_808)
        bond_creator.connect_atoms()

    def test_single_atom(self):
        self.assertEqual(True, find_ligand_in_mof(self.carbon, self.carbon), "Carbon should be subgraph of Carbon")
        self.assertEqual(True, find_ligand_in_mof(self.iron, self.iron), "Iron should be subgraph of Iron")
        self.assertEqual(False, find_ligand_in_mof(self.carbon, self.iron), "Carbon should not be subgraph of Iron")
        self.assertEqual(False, find_ligand_in_mof(self.iron, self.carbon), "Iron should not be subgraph of Carbon")

    def test_atom_in_ligand(self):
        self.assertEqual(True, find_ligand_in_mof(self.carbon, self.benzene), "Carbon should be subgraph of Benzene")
        self.assertEqual(False, find_ligand_in_mof(self.iron, self.benzene), "Iron should not be subgraph of Benzene")

    def test_ligand_in_ligand(self):
        self.assertEqual(True, find_ligand_in_mof(self.benzene, self.solitary_benzene), "Benzene(6C) should be "
                                                                                        "subgraph of Benzene(6C, 6H")
        self.assertEqual(False, find_ligand_in_mof(self.solitary_benzene, self.benzene), "Not other way around")

    def test_ligand_in_mof(self):
        self.assertEqual(True, find_ligand_in_mof(self.benzene, self.mof_808), "Benzene(6C) should be in mof")
        self.assertEqual(False, find_ligand_in_mof(self.solitary_benzene, self.mof_808), "Filled Benzene(6C, 6H) "
                                                                                         "should not be in mof")

if __name__ == '__main__':
    unittest.main()
