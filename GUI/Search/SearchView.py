import tkinter as tk
import tkinter.ttk as ttk
import re
from pathlib import Path

from GUI.Search import Attributes
from GUI.Utility import MultipleAutoCompleteSearch, FrameWithProcess, Tooltips
from GUI.Search.SearchTerms import SearchTerms, search_in_mofsForTests
from MofIdentifier import SearchMOF
from MofIdentifier.fileIO import LigandReader
from MofIdentifier.subbuilding import SBUCollectionManager

ROW_MAXIMUM = 6


class View(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda search: self.search_from_input(search), height=40, width=300, padx=12)
        self.attribute_entries = list()
        self.custom_ligands = dict()
        self.search_to_results = dict()
        self.text_to_search = dict()
        for i in range(8 + 1):
            self.grid_columnconfigure(i, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.lbl_label = tk.Label(self, text="Name must contain: ")
        self.lbl_label.grid(row=0, column=0, pady=2, sticky=tk.NE)
        self.ent_label = tk.Entry(self)
        self.ent_label.grid(row=0, column=1, pady=2, sticky=tk.NW)

        self.lbl_ligand = tk.Label(self, text="Required Ligands: ")
        self.lbl_ligand.grid(row=1, column=0, pady=2, sticky=tk.NE)
        self.ent_ligand = MultipleAutoCompleteSearch.View(self, self.focus_ligand)
        self.ent_ligand.set_possible_values(self.all_ligands_names())
        self.ent_ligand.grid(row=1, column=1, pady=2, sticky=tk.EW)
        self.ent_ligand.initial_combobox.focus_set()
        self.lbl_elements = tk.Label(self, text="Required Elements: ")
        self.lbl_elements.grid(row=1, column=2, pady=2, sticky=tk.E, padx=(4, 0))
        self.ent_elements = tk.Entry(self)
        self.ent_elements.insert(0, 'C, H')
        self.ent_elements.grid(row=1, column=3, pady=2, padx=(0, 4), sticky=tk.W)
        self.lbl_sbus = tk.Label(self, text="Required SBUs: ")
        self.lbl_sbus.grid(row=1, column=4, pady=2, sticky=tk.NE)
        self.ent_sbus = MultipleAutoCompleteSearch.View(self, self.focus_sbu)
        self.ent_sbus.set_possible_values(self.all_sbu_names())
        self.ent_sbus.grid(row=1, column=5, pady=2, sticky=tk.EW)

        small_font = ("Arial", 8)
        self.lbl_excl_ligand = tk.Label(self, text="Forbidden Ligands: ", font=small_font)
        self.lbl_excl_ligand.grid(row=2, column=0, pady=2, sticky=tk.NE)
        self.ent_excl_ligand = MultipleAutoCompleteSearch.View(self, self.focus_ligand, small_font)
        self.ent_excl_ligand.set_possible_values(self.all_ligands_names())
        self.ent_excl_ligand.grid(row=2, column=1, pady=2, sticky=tk.W)
        self.lbl_excl_elements = tk.Label(self, text="Forbidden Elements: ", font=small_font)
        self.lbl_excl_elements.grid(row=2, column=2, sticky=tk.E)
        self.ent_excl_elements = tk.Entry(self, width=10, font=small_font)
        self.ent_excl_elements.insert(0, '')
        self.ent_excl_elements.grid(row=2, column=3, pady=2, sticky=tk.W)
        self.lbl_excl_sbus = tk.Label(self, text="Forbidden SBUs: ", font=small_font)
        self.lbl_excl_sbus.grid(row=2, column=4, pady=2, sticky=tk.NE)
        self.ent_excl_sbus = MultipleAutoCompleteSearch.View(self, self.focus_sbu, small_font)
        self.ent_excl_sbus.set_possible_values(self.all_sbu_names())
        self.ent_excl_sbus.grid(row=2, column=5, pady=2, sticky=tk.W)

        self.attribute_row = None
        self.add_attribute_search_entries()  # Row 3

        self.lbl_redo_search = tk.Label(self, text="Previous searches: ")
        self.lbl_redo_search.grid(row=4, column=0, pady=2)
        self.redo_search_selected = tk.StringVar()
        self.redo_search_selected.set('History')
        self.dropdown_redo_search = ttk.OptionMenu(self, self.redo_search_selected, *self.search_to_results.keys())
        self.dropdown_redo_search.grid(row=4, column=1, pady=2, sticky=tk.EW, columnspan=4)
        self.btn_redo_search = tk.Button(self, text="Redo", command=self.redo_search)
        self.btn_redo_search.grid(row=4, column=5, pady=2)

        self.btn_clear = tk.Button(self, text="Clear", command=self.clear)
        self.btn_clear.grid(row=ROW_MAXIMUM - 1, column=0, pady=2, columnspan=1)
        self.btn_search = tk.Button(self, text="Search", command=self.start_process, font=('Arial', 16), bd=4)
        self.btn_search.grid(row=ROW_MAXIMUM - 1, column=0, pady=2, columnspan=12)


    def clear(self):
        for entry in self.attribute_entries:
            entry.max.delete(0, tk.END)
            entry.min.delete(0, tk.END)
        self.ent_ligand.clear()
        self.ent_excl_ligand.clear()
        self.ent_elements.delete(0, tk.END)
        self.ent_excl_elements.delete(0, tk.END)
        self.ent_sbus.clear()
        self.ent_excl_sbus.clear()

    def force_search_ligand(self, ligand):
        search = SearchTerms(ligands=[ligand])
        self.start_process(search)

    def force_search_sbu(self, sbu):
        search = SearchTerms(sbus=[sbu])
        self.start_process(search)

    def redo_search(self):
        search_text = self.redo_search_selected.get()
        if search_text == 'History':
            return
        search = self.text_to_search[search_text]
        if self.search_to_results[search] is not None:
            self.parent.display_search_results(self.search_to_results[search])
        else:
            self.start_process(search)

    def get_ligands(self, ligand_names):
        ligands = list()
        other_ligands = list()
        for ligand_name in ligand_names:
            if ligand_name in self.custom_ligands:
                ligands.append(self.custom_ligands[ligand_name])
            else:
                other_ligands.append(ligand_name)
        ligands.extend(SearchMOF.read_ligands_from_files(other_ligands))
        return ligands

    def get_sbus(self, sbu_names):
        sbus = list()
        other_sbus = list()
        for sbu_name in sbu_names:
            if sbu_name in self.custom_ligands:
                sbus.append(self.custom_ligands[sbu_name])
            else:
                other_sbus.append(sbu_name)
        sbus.extend(SBUCollectionManager.read_sbus_from_files(other_sbus))
        return sbus

    def search_from_input(self, search):
        # Generate SearchTerms object from entries if needed
        if search is None:
            ligands = self.get_ligands(self.ent_ligand.get_values())
            forbidden_ligands = self.get_ligands(self.ent_excl_ligand.get_values())
            sbus = self.get_sbus(self.ent_sbus.get_values())
            forbidden_sbus = self.get_sbus(self.ent_excl_sbus.get_values())
            element_symbols_text = self.ent_elements.get()
            element_symbols = re.findall(r"[\w']+", element_symbols_text)
            forbidden_element_symbols_text = self.ent_excl_elements.get()
            forbidden_element_symbols = re.findall(r"[\w']+", forbidden_element_symbols_text)
            attributes = self.get_attribute_parameters()
            label_substring = self.ent_label.get()
            search = SearchTerms(ligands, element_symbols, forbidden_ligands, forbidden_element_symbols,
                                 sbus, forbidden_sbus, attributes, label_substring)
        # Shortcut evaluation if possible
        if search in self.search_to_results and self.search_to_results[search] is not None \
                and self.search_to_results[search] != 'ongoing':
            self.parent.display_search_results(self.search_to_results[search])
        else:
            self.text_to_search[str(search)] = search
            self.dropdown_redo_search['menu'].add_command(label=str(search), command=lambda value=str(search):
                                                            self.redo_search_selected.set(value))
            self.search_to_results[search] = 'ongoing'
            results = search_in_mofsForTests(search)  # TODO: this will change with db integration
            self.search_to_results[search] = results
            self.parent.display_search_results(results)

    def add_custom_ligand(self, mol):
        self.ent_ligand.add_new_possible_value('* ' + mol.label)
        self.custom_ligands['* ' + mol.label] = mol
        self.ent_sbus.add_new_possible_value('* ' + mol.label)
        self.ent_excl_ligand.add_new_possible_value('* ' + mol.label)
        self.ent_excl_sbus.add_new_possible_value('* ' + mol.label)

    def add_attribute_search_entries(self):
        def attribute_heading(parent):
            view = tk.Frame(parent)
            top = tk.Label(view, text='')
            top.pack()
            middle = tk.Label(view, text='Maximum')
            middle.pack()
            bottom = tk.Label(view, text='Minimum')
            bottom.pack()
            return view

        self.attribute_row = tk.Frame(self)
        attribute_heading(self.attribute_row).pack(side='left')
        for attr in Attributes.attributes:
            if Attributes.attributes[attr].enabled:
                entry = AttributeEntry(self.attribute_row, attr, Attributes.attributes[attr].description)
                self.attribute_entries.append(entry)
                entry.pack(side='left')
        self.attribute_row.grid(column=0, row=3, columnspan=12, pady=2)

    def get_attribute_parameters(self):
        return {entry.name: entry.get() for entry in self.attribute_entries}  # FIXME: don't use deselected attributes

    def all_ligands_names(self):  # Will change with adding DB
        path = str(Path(__file__).parent / "../../MofIdentifier/ligands")
        ligands = LigandReader.get_all_mols_from_directory(path)
        return [ligand.label for ligand in ligands]

    def all_sbu_names(self):  # Will change with adding DB
        path_1 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/cluster")
        path_2 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/connector")
        path_3 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/auxiliary")
        sbus = LigandReader.get_all_mols_from_directory(path_1) + \
               LigandReader.get_all_mols_from_directory(path_2) + \
               LigandReader.get_all_mols_from_directory(path_3)
        return [sbu.label for sbu in sbus]

    def add_error_to_layout(self, error_row):
        error_row.grid(row=ROW_MAXIMUM + 1, column=0, pady=2, columnspan=12, sticky=tk.EW)

    def add_progress_to_layout(self, progress):
        progress.grid(row=ROW_MAXIMUM, column=0, pady=2, columnspan=12, sticky=tk.EW)

    def add_cancel_to_layout(self, btn_cancel):
        btn_cancel.grid(row=ROW_MAXIMUM - 1, column=4, pady=2, columnspan=1)

    def focus_ligand(self, ligand_name):
        if ligand_name != '':
            try:
                ligand = self.get_ligands([ligand_name])[0]
                self.parent.highlight_molecule(ligand)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def focus_sbu(self, sbu_name):
        if sbu_name != '':
            try:
                sbu = self.get_sbus([sbu_name])[0]
                self.parent.highlight_molecule(sbu)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def regenerate_attribute_row(self):
        self.attribute_row.grid_forget()
        self.attribute_entries = list()
        self.add_attribute_search_entries()


class AttributeEntry(tk.Frame):
    def __init__(self, parent, name, description):
        self.parent = parent
        self.name = name
        tk.Frame.__init__(self, self.parent, bd=1, relief=tk.SOLID)
        self.top = tk.Label(self, text=name)
        Tooltips.create_tool_tip(self.top, description)
        self.top.grid()
        vcmd = (self.register(self.is_numeric_input))
        self.max = tk.Entry(self, validate='key', validatecommand=(vcmd, '%P'), width=max(7, len(name)))
        self.max.grid(padx=4)
        self.min = tk.Entry(self, validate='key', validatecommand=(vcmd, '%P'), width=max(7, len(name)))
        self.min.grid(padx=4)

    def is_numeric_input(self, P):
        if len(P) == 0:
            return True
        elif '0123456789.-+e'.find(P[-1]) >= 0:
            try:
                float(P + '5')  # could be any number. This allows user to type a valid number whose parts aren't valid
                return True
            except ValueError as v:
                return False
        else:
            return False

    def get(self):
        if len(self.max.get()) == 0:
            max = None
        else:
            max = float(self.max.get())
        if len(self.min.get()) == 0:
            min = None
        else:
            min = float(self.min.get())
        return min, max
