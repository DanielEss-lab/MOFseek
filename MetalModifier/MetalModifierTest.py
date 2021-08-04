import unittest

from MetalModifier.main import replace_metal, count_added_protons, protons_needed
from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


def count_node_protons(mof):
    clusters = SBUIdentifier.split(mof, True).nodes_with_auxiliaries().items()
    clusters = [cluster for cluster in clusters if len(cluster[0].atoms) > 1]
    assert (len(clusters) > 0)
    assert (all(cluster[0] == clusters[0][0] for cluster in clusters))
    num_protons = count_added_protons(clusters[0])
    return num_protons


class WriteAtomTest(unittest.TestCase):
    def test_cartesian_to_fractional(self):
        replace_metal(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif',
                      r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif', 'Y')
        mof = CifReader.get_mof(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif')
        original_atom = mof.atoms[0]
        fractional_atom = Atom.from_fractional(original_atom.label, original_atom.type_symbol, original_atom.a,
                                               original_atom.b, original_atom.c, mof.angles, mof.fractional_lengths)
        cartesian_atom = Atom.from_cartesian(original_atom.label, original_atom.type_symbol, original_atom.x,
                                             original_atom.y, original_atom.z, mof)
        self.assertAlmostEqual(original_atom.x, fractional_atom.x)
        self.assertAlmostEqual(original_atom.x, cartesian_atom.x)
        self.assertAlmostEqual(original_atom.a, fractional_atom.a)
        self.assertAlmostEqual(original_atom.a, cartesian_atom.a)


class ChangeMetalTest(unittest.TestCase):
    def test_Zr_to_Y(self):
        replace_metal(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif',
                      r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif', 'Y')
        new_mof = CifReader.get_mof(r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif')
        self.assertTrue('Y' in new_mof.atoms_string())
        self.assertEqual(protons_needed('Y'), count_node_protons(new_mof))

    def test_Zr_to_V(self):
        replace_metal(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif',
                      r'C:\Users\mdavid4\Downloads\smod7-except-V.cif', 'V')
        new_mof = CifReader.get_mof(r'C:\Users\mdavid4\Downloads\smod7-except-V.cif')
        self.assertTrue('V' in new_mof.atoms_string())
        self.assertEqual(protons_needed('V'), count_node_protons(new_mof))


if __name__ == '__main__':
    unittest.main()