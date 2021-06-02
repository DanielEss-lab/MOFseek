import threading
import tkinter as tk
import tkinter.ttk as ttk
import re
from pathlib import Path

from GUI import UploadLigandView, MultipleAutoCompleteSearch
from GUI import AutoCompleteComboBox
from MofIdentifier import SearchMOF
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader, LigandReader


class SearchTerms:
    def __init__(self, ligands, element_symbol_list, excl_ligands, excl_elements):
        self.ligands = ligands
        self.element_symbols = element_symbol_list
        self.excl_ligands = excl_ligands
        self.excl_element_symbols = excl_elements
        # Add parameters here

    def passes(self, MOF):
        for element in self.element_symbols:
            if element not in MOF.elementsPresent:
                return False
        for element in self.excl_element_symbols:
            if element in MOF.elementsPresent:
                return False
        return SubGraphMatcher.mof_has_all_ligands(MOF, self.ligands) \
            and SubGraphMatcher.mof_has_no_ligands(MOF, self.excl_ligands)


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

        self.lbl_ligand = tk.Label(self, text="Required Ligands: ")
        self.lbl_ligand.grid(row=1, column=0, pady=2, sticky=tk.E)
        self.ent_ligand = MultipleAutoCompleteSearch.View(self)
        self.ent_ligand.set_possible_values(self.all_ligands_names())
        self.ent_ligand.grid(row=1, column=1, pady=2, sticky=tk.EW)
        self.ent_ligand.initial_combobox.focus_set()
        self.lbl_elements = tk.Label(self, text="Required Elements: ")
        self.lbl_elements.grid(row=1, column=2, pady=2, sticky=tk.E)
        self.ent_elements = tk.Entry(self)
        self.ent_elements.insert(0, 'C, H')
        self.ent_elements.grid(row=1, column=3, pady=2, sticky=tk.EW)

        self.lbl_excl_ligand = tk.Label(self, text="Forbidden Ligands: ")
        self.lbl_excl_ligand.grid(row=2, column=0, pady=2, sticky=tk.E)
        self.ent_excl_ligand = MultipleAutoCompleteSearch.View(self)
        self.ent_excl_ligand.set_possible_values(self.all_ligands_names())
        self.ent_excl_ligand.grid(row=2, column=1, pady=2, sticky=tk.EW)
        self.ent_excl_ligand.initial_combobox.focus_set()
        self.lbl_excl_elements = tk.Label(self, text="Forbidden Elements: ")
        self.lbl_excl_elements.grid(row=2, column=2, pady=2, sticky=tk.E)
        self.ent_excl_elements = tk.Entry(self)
        self.ent_excl_elements.insert(0, '')
        self.ent_excl_elements.grid(row=2, column=3, pady=2, sticky=tk.EW)

        self.add_attribute_search_entries()  # Row 3

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        btn_clear = tk.Button(self, text="Clear", command=self.clear)
        btn_clear.grid(row=4, column=0, pady=2, columnspan=1)
        btn_search = tk.Button(self, text="Search", command=self.perform_search)
        btn_search.grid(row=4, column=0, pady=2, columnspan=12)

    def clear(self):
        for entry in self.attribute_entries:
            entry.max.delete(0, tk.END)
            entry.min.delete(0, tk.END)
        self.ent_ligand.clear()
        self.ent_elements.delete(0, tk.END)

    def perform_search(self):
        def callback():
            self.progress.start()
            self.search_from_input()
            self.progress.stop()
            self.progress.grid_forget()

        self.progress.grid(row=5, column=0, pady=2, columnspan=12, sticky=tk.EW)
        threading.Thread(target=callback).start()

    def search_from_input(self):
        def get_ligands(multiple_auto_combobox):
            ligand_names = multiple_auto_combobox.get_values()

            ligands = list()
            other_ligands = list()
            for ligand_name in ligand_names:
                if ligand_name in self.custom_ligands:
                    ligands.append(self.custom_ligands[ligand_name])
                else:
                    other_ligands.append(ligand_name)
            ligands.extend(SearchMOF.read_ligands_from_files(other_ligands))
            return ligands

        ligands = get_ligands(self.ent_ligand)
        forbidden_ligands = get_ligands(self.ent_excl_ligand)
        element_symbols_text = self.ent_elements.get()
        element_symbols = re.findall(r"[\w']+", element_symbols_text)
        forbidden_element_symbols_text = self.ent_excl_elements.get()
        forbidden_element_symbols = re.findall(r"[\w']+", forbidden_element_symbols_text)
        search = SearchTerms(ligands, element_symbols, forbidden_ligands, forbidden_element_symbols)
        results = search_ligand_names_in_mofsForTests(search)
        self.parent.display_search_results(results)

    def add_custom_ligand(self, mol):
        self.ent_ligand.add_new_possible_value('* ' + mol.label)
        self.custom_ligands['* ' + mol.label] = mol

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
        # attribute_row.grid(column=0, row=2, columnspan=12, pady=2)  # TODO: add back in when ready

    def all_ligands_names(self):  # Will change with adding DB
        path = str(Path(__file__).parent / "../MofIdentifier/ligandsWildCards")
        ligands = LigandReader.get_all_mols_from_directory(path)
        return [ligand.label for ligand in ligands]


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
