import unittest

from MetalModifier.main import replace_metal, count_added_protons, protons_needed
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


def count_node_protons(mof):
    clusters = SBUIdentifier.split(mof, True).nodes_with_auxiliaries().items()
    clusters = [cluster for cluster in clusters if len(cluster[0].atoms) > 1]
    assert (len(clusters) > 0)
    assert (all(cluster[0] == clusters[0][0] for cluster in clusters))
    num_protons = count_added_protons(clusters[0])
    return num_protons


class MyTestCase(unittest.TestCase):
    def test_change_metal(self):
        replace_metal(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests\smod7-pos-1.cif',
                      r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif', 'Y')
        new_mof = CifReader.get_mof(r'C:\Users\mdavid4\Downloads\smod7-except-Y.cif')
        self.assertTrue('Y' in new_mof.atoms_string())
        self.assertEqual(protons_needed('Y'), count_node_protons(new_mof))


if __name__ == '__main__':
    unittest.main()
