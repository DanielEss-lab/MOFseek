import unittest

from MetalModifier.main import replace_metal
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


class MyTestCase(unittest.TestCase):
    def test_change_metal(self):
        replace_metal(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif',
                      r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif', 'Y')
        new_mof = CifReader.get_mof(r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif')
        nodes = SBUIdentifier.split(new_mof, True).clusters
        self.assertTrue('Y' in new_mof.atoms_string())
        atoms_in_node = new_mof.sbus().clusters[0].atoms
        self.assertEqual(16, len(atoms_in_node))


if __name__ == '__main__':
    unittest.main()
