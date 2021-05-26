import tkinter as tk
from pathlib import Path

from MofIdentifier import SearchMOF
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader


def search_ligand_names_in_mofsForTests(names):
    ligands = SearchMOF.read_ligands_from_files(names)
    path = str(Path(__file__).parent / "../MofIdentifier/mofsForTests")
    mofs = CifReader.get_all_mofs_in_directory(path)
    good_mofs = [mof for mof in mofs if SubGraphMatcher.mof_has_all_ligands(mof, ligands)]
    return good_mofs


def make_view(parent):
    view = tk.Frame(parent, height=40, width=300, bd=2, relief=tk.SOLID)
    lbl_ligand = tk.Label(view, text="Ligands: ")
    lbl_ligand.pack(side='left')
    ent_ligand = tk.Entry(view)
    ent_ligand.pack(side='left')

    def search_from_input():
        names_string = [ent_ligand.get()]
        results = search_ligand_names_in_mofsForTests(names_string)
        parent.display_search_results(results)
    btn_search = tk.Button(view, text="Search", command=search_from_input)
    btn_search.pack(side='right')

    return view
