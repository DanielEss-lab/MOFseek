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
        cls.benzene = XyzReader.read_xyz('BenzeneBase.xyz')
        bond_creator.connect_atoms(cls.benzene)
        cls.solitary_benzene = XyzReader.read_xyz('Benzene.xyz')
        bond_creator.connect_atoms(cls.solitary_benzene)
        cls.mof_808 = CifReader.read_mof('smod7-pos-1.cif')
        bond_creator = MofBondCreator(cls.mof_808)
        bond_creator.connect_atoms()

    def test_something(self):
        self.assertEqual(True, find_ligand_in_mof(self.carbon, self.mof_808))


if __name__ == '__main__':
    unittest.main()
