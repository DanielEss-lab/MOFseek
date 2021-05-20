import time
import unittest
from pathlib import Path

from MofIdentifier import SearchMOF, StrongSubGraphMatcher, WeakSubGraphMatcher
from MofIdentifier.fileIO import SmilesReader, CifReader


class SearchMofTest(unittest.TestCase):
    def test_M6_node_mofs(self):
        user_path = str(Path(__file__).parent / "mofsForTests")
        ligand_file_names = ["M6_node.xyz", "H2O_1.xyz"]
        ligands = SearchMOF.read_ligands_from_files(ligand_file_names)
        mofs = CifReader.get_all_mofs_in_directory(user_path)
        good_mofs = StrongSubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
        self.assertEqual(4, len(good_mofs))

    def test_SMILES_in_M6_mofs(self):
        user_path = str(Path(__file__).parent / "mofsForTests" / "M6 MOFs")
        ligands = [SmilesReader.mol_from_str('C1=CC=CC=C1')]
        mofs = CifReader.get_all_mofs_in_directory(user_path)
        print('Filtering for subgraph isomorphism...')
        good_mofs = WeakSubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
        mof_names = map(lambda x: x.label, good_mofs)
        print(*ligands, " present in the following file(s):")
        print(*mof_names, sep="\n")
        time.sleep(1)
        assert True



if __name__ == '__main__':
    unittest.main()
