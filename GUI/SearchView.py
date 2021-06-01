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
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=40, width=300, bd=2, relief=tk.SOLID)
        self.attribute_entries = list()
        self.custom_ligands = dict()

        for i in range(8 + 1):
            self.grid_columnconfigure(i, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.upload_mof_v = UploadLigandView.View(self)
        self.upload_mof_v.grid(row=0, column=0, pady=2, columnspan=12)
        self.lbl_ligand = tk.Label(self, text="Ligands: ")
        self.lbl_ligand.grid(row=1, column=0, pady=2, sticky=tk.E)
        self.ent_ligand = tk.Entry(self)
        self.ent_ligand.insert(0, 'H2O_1.xyz')
        self.ent_ligand.grid(row=1, column=1, pady=2, sticky=tk.EW)
        self.lbl_elements = tk.Label(self, text="Elements: ")
        self.lbl_elements.grid(row=1, column=2, pady=2, sticky=tk.E)
        self.ent_elements = tk.Entry(self)
        self.ent_elements.insert(0, 'N')
        self.ent_elements.grid(row=1, column=3, pady=2, sticky=tk.EW)
        self.add_attribute_search_entries()

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        btn_clear = tk.Button(self, text="Clear", command=self.clear)
        btn_clear.grid(row=3, column=0, pady=2, columnspan=1)
        btn_search = tk.Button(self, text="Search", command=self.perform_search)
        btn_search.grid(row=3, column=0, pady=2, columnspan=12)

    def clear(self):
        for entry in self.attribute_entries:
            entry.max.delete(0, tk.END)
            entry.min.delete(0, tk.END)
        self.ent_ligand.delete(0, tk.END)
        self.ent_elements.delete(0, tk.END)


    def perform_search(self):
        def callback():
            self.progress.start()
            self.search_from_input()
            self.progress.stop()
            self.progress.grid_forget()
        self.progress.grid(row=4, column=0, pady=2, columnspan=12, sticky=tk.EW)
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

    def add_attribute_search_entries(self):
        def attribute_heading(parent):
            view = tk.Frame(parent, bd=1, relief=tk.SOLID)
            top = tk.Label(view, text='')
            top.pack()
            middle = tk.Label(view, text='Maximum')
            middle.pack()
            bottom = tk.Label(view, text='Minimum')
            bottom.pack()
            return view

        attributes = [
            "Pore Size (mm):",
            "Surface Area (mm):",
            "Volume (mL/mol)",
            "Conductivity (Ohms)",
            "Fav Food",
            "Weight (mG)",
            "Postal Code",
            "Fictitious val",
        ]
        attribute_row = tk.Frame(self)
        attribute_heading(attribute_row).pack(side='left')
        for idx, text in enumerate(attributes):
            entry = AttributeEntry(attribute_row, text)
            self.attribute_entries.append(entry)
            entry.pack(side='left')
        # attribute_row.grid(column=0, row=2, columnspan=12, pady=2) #TODO: add back in when ready


class AttributeEntry(tk.Frame):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        tk.Frame.__init__(self, self.parent, bd=1, relief=tk.SOLID)
        self.top = tk.Label(self, text=name)
        self.top.pack()
        self.max = tk.Entry(self)
        self.max.pack()
        self.min = tk.Entry(self)
        self.min.pack()
