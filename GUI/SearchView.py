import threading
import tkinter as tk
import tkinter.ttk as ttk
import re
from pathlib import Path

from GUI import UploadLigandView
from MofIdentifier import SearchMOF
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader


class SearchTerms:
    def __init__(self, ligands, element_symbol_list):
        self.ligands = ligands
        self.element_symbols = element_symbol_list
        # Add parameters here

    def passes(self, MOF):
        for element in self.element_symbols:
            if element not in MOF.elementsPresent:
                return False
        return SubGraphMatcher.mof_has_all_ligands(MOF, self.ligands)


def search_ligand_names_in_mofsForTests(search):
    path = str(Path(__file__).parent / "../MofIdentifier/mofsForTests")
    mofs = CifReader.get_all_mofs_in_directory(path)
    good_mofs = [mof for mof in mofs if search.passes(mof)]
    return good_mofs


class View(tk.Frame):
    def __init__(self, parent):
        self.custom_ligands = dict()
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=40, width=300, bd=2, relief=tk.SOLID)
        self.upload_mof_v = UploadLigandView.View(self)
        self.upload_mof_v.grid(row=0, column=0, pady=2, columnspan=7)
        self.lbl_ligand = tk.Label(self, text="Ligands: ")
        self.lbl_ligand.grid(row=1, column=0, pady=2)
        self.ent_ligand = tk.Entry(self)
        self.ent_ligand.insert(0, 'H2O_1.xyz')
        self.ent_ligand.grid(row=1, column=1, pady=2)
        self.lbl_elements = tk.Label(self, text="Elements: ")
        self.lbl_elements.grid(row=1, column=2, pady=2)
        self.ent_elements = tk.Entry(self)
        self.ent_elements.insert(0, 'N')
        self.ent_elements.grid(row=1, column=3, pady=2)
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='indeterminate')

        btn_search = tk.Button(self, text="Search", command=self.perform_search)
        btn_search.grid(row=1, column=4, pady=2)

    def perform_search(self):
        def callback():
            self.progress.start()
            self.search_from_input()
            self.progress.stop()
            self.progress.grid_forget()
        self.progress.grid(row=2, column=0, pady=2, columnspan=7, sticky=tk.EW)
        threading.Thread(target=callback).start()

    def search_from_input(self):
        ligand_names_text = self.ent_ligand.get().replace(',', ' ')
        ligand_names = [name for name in ligand_names_text.split(' ') if len(name) > 0]

        ligands = list()
        other_ligands = list()
        for ligand_name in ligand_names:
            if ligand_name in self.custom_ligands:
                ligands.append(self.custom_ligands[ligand_name])
            else:
                other_ligands.append(ligand_name)
        ligands.extend(SearchMOF.read_ligands_from_files(other_ligands))

        element_symbols_text = self.ent_elements.get()
        element_symbols = re.findall(r"[\w']+", element_symbols_text)
        search = SearchTerms(ligands, element_symbols)
        results = search_ligand_names_in_mofsForTests(search)
        self.parent.display_search_results(results)

    def add_custom_ligand(self, mol):
        pretext = ', ' if len(self.ent_ligand.get()) > 0 else ''
        self.ent_ligand.insert(tk.END, pretext + mol.label)
        self.custom_ligands[mol.label] = mol
