import os
import unittest
from pathlib import Path

from MofIdentifier import SearchMOF, SubGraphMatcher


class SearchMofTest(unittest.TestCase):
    def test_M6_node_mofs(self):
        user_path = str(Path(__file__).parent / "mofsForTests")
        ligand_file_names = ["M6_node.xyz", "H2O_1.xyz"]
        ligands = SearchMOF.read_ligands_from_files(ligand_file_names)
        mofs = SearchMOF.get_all_mofs_in_directory(user_path)
        good_mofs = SubGraphMatcher.filter_for_mofs_with_ligands(mofs, ligands)
        self.assertEqual(4, len(good_mofs))


if __name__ == '__main__':
    unittest.main()
