from unittest import TestCase

from MofIdentifier.SubGraphMatching import CustomWildcard, SubGraphMatcher
from MofIdentifier.fileIO import CifReader, LigandReader


class TestWC(TestCase):
    def test_matches(self):
        Wc1 = CustomWildcard.WC('Wca', True, ['Cd', 'Ca', 'Fe'])
        Wc2 = CustomWildcard.WC('Wcb', False, ['H'])
        self.assertTrue(Wc1.matches('Cd') and Wc1.matches('Ca') and Wc1.matches('Fe'))
        self.assertFalse(Wc1.matches('H') or Wc1.matches('C') or Wc1.matches('V'))
        self.assertTrue(Wc2.matches('Cd') and Wc2.matches('Ca') and Wc2.matches('Fe')
                        and Wc2.matches('C') and Wc2.matches('V'))
        self.assertFalse(Wc2.matches('H'))

    def test_parse_line(self):
        expected = {'Wca': CustomWildcard.WC('Wca', True, ['Cd', 'Ca', 'Fe']),
                    'Wcb': CustomWildcard.WC('Wcb', False, ['H'])}
        wildcards = CustomWildcard.WC.parse_line("Wca=Cd,Ca,Fe;Wcb=notH")
        self.assertCountEqual(expected, wildcards)

    def test_ligand_within_mof(self):
        mof = CifReader.get_mof('../mofsForTests/smod7-pos-1.cif')
        smiles_ligand = LigandReader.get_mol_from_file('../ligands/test_resources/O_by_two_non_H.smiles')
        xyz_ligand = LigandReader.get_mol_from_file('../ligands/test_resources/O_by_two_non_H.xyz')
        self.assertTrue(SubGraphMatcher.find_ligand_in_mof(smiles_ligand, mof))
        self.assertTrue(SubGraphMatcher.find_ligand_in_mof(xyz_ligand, mof))
