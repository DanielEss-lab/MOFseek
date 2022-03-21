import platform
import tkinter as tk
import tkinter.font as tkFont

import re
from tkinter import ttk

from GUI import Attributes, Settings
from GUI.Utility import MultipleAutoCompleteSearch, FrameWithProcess, Tooltips, StyledButton
from GUI.Pages.Search.SearchTerms import SearchTerms
from DAOsAndServices import MOFDAO, SBUDAO, LigandDAO


ROW_MAXIMUM = 6


class View(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda search: self.search_from_input(search), height=40, width=300, padx=12)
        self.attribute_entries = list()
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
        # self.ent_elements.insert(0, 'C, H')
        self.ent_elements.grid(row=1, column=3, pady=2, padx=(0, 4), sticky=tk.W)
        self.lbl_sbus = tk.Label(self, text="Required SBUs: ")
        # self.lbl_sbus.grid(row=1, column=4, pady=2, sticky=tk.NE)
        self.ent_sbus = MultipleAutoCompleteSearch.View(self, self.focus_sbu)
        self.ent_sbus.set_possible_values(self.all_sbu_names())
        # self.ent_sbus.grid(row=1, column=5, pady=2, sticky=tk.EW)

        f_size = tkFont.Font(self.lbl_ligand, self.lbl_ligand["font"])['size']
        small_font = ("Arial", f_size - 2)
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
        # self.lbl_excl_sbus.grid(row=2, column=4, pady=2, sticky=tk.NE)
        self.ent_excl_sbus = MultipleAutoCompleteSearch.View(self, self.focus_sbu, small_font)
        self.ent_excl_sbus.set_possible_values(self.all_sbu_names())
        # self.ent_excl_sbus.grid(row=2, column=5, pady=2, sticky=tk.W)

        self.attribute_row = None
        self.add_attribute_search_entries()  # Row 3

        self.lbl_redo_search = tk.Label(self, text="Previous searches: ")
        self.lbl_redo_search.grid(row=4, column=0, pady=2)
        self.redo_search_selected = tk.StringVar()
        self.redo_search_selected.set('History')
        if platform.system() == 'Darwin':
            self.dropdown_redo_search = tk.OptionMenu(self, self.redo_search_selected, *self.search_to_results,
                                                      value='History')
        else:
            self.dropdown_redo_search = ttk.OptionMenu(self, self.redo_search_selected, *self.search_to_results)
        self.dropdown_redo_search.grid(row=4, column=1, pady=2, sticky=tk.EW, columnspan=4)
        self.btn_redo_search = StyledButton.make(self, text="Redo", command=self.redo_search)
        self.btn_redo_search.grid(row=4, column=5, pady=2)

        self.btn_clear = StyledButton.make(self, text="Clear", command=self.clear)
        self.btn_clear.grid(row=ROW_MAXIMUM - 1, column=0, pady=2, columnspan=1)
        self.btn_search = StyledButton.make(self, text="Search", command=self.start_process, font=('Arial', f_size * 2))
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

    def force_search_ligand(self, ligand: str):
        search = SearchTerms(ligands=[ligand])
        self.start_process(search)

    def force_search_sbu(self, sbu: str):
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

    def search_from_input(self, search):
        # Generate SearchTerms object from entries if needed
        if search is None:
            ligands = self.ent_ligand.get_values()
            forbidden_ligands = self.ent_excl_ligand.get_values()
            sbus = self.ent_sbus.get_values()
            forbidden_sbus = self.ent_excl_sbus.get_values()
            element_symbols_text = self.ent_elements.get()
            element_symbols = re.findall(r"[\w']+", element_symbols_text)
            forbidden_element_symbols_text = self.ent_excl_elements.get()
            forbidden_element_symbols = re.findall(r"[\w']+", forbidden_element_symbols_text)
            attributes = self.get_attribute_parameters()
            label_substring = self.ent_label.get()
            search = SearchTerms(ligands, forbidden_ligands, element_symbols, forbidden_element_symbols,
                                 sbus, forbidden_sbus, attributes, label_substring, sources=Settings.current_source_states())
        # Shortcut evaluation if possible
        if search in self.search_to_results and self.search_to_results[search] is not None \
                and self.search_to_results[search] != 'ongoing':
            self.parent.display_search_results(self.search_to_results[search])
        else:
            self.text_to_search[str(search)] = search
            self.dropdown_redo_search['menu'].add_command(label=str(search), command=lambda value=str(search):
            self.redo_search_selected.set(value))
            self.search_to_results[search] = 'ongoing'
            results = MOFDAO.get_passing_MOFs(search)
            self.search_to_results[search] = results
            self.parent.display_search_results(results)

    def add_attribute_search_entries(self):
        def attribute_heading(parent):
            view = tk.Frame(parent)
            top = tk.Label(view, text='')
            top.pack()
            middle = tk.Label(view, text='Maximum/Include')
            middle.pack()
            bottom = tk.Label(view, text='Minimum/Exclude')
            bottom.pack()
            return view

        self.attribute_row = tk.Frame(self)
        attribute_heading(self.attribute_row).pack(side='left')
        for name, attr in Attributes.attributes.items():
            if Settings.attribute_is_enabled[name]:
                entry = make_attribute_entry(self.attribute_row, name, attr)
                self.attribute_entries.append(entry)
                entry.pack(side='left')
        self.attribute_row.grid(column=0, row=3, columnspan=12, pady=2)

    def get_attribute_parameters(self):
        return {entry.name: entry.get() for entry in self.attribute_entries}

    def all_ligands_names(self):
        return LigandDAO.get_all_names()

    def all_sbu_names(self):
        return SBUDAO.get_all_names()

    def add_error_to_layout(self, error_row):
        error_row.grid(row=ROW_MAXIMUM + 1, column=0, pady=2, columnspan=12, sticky=tk.EW)

    def add_progress_to_layout(self, progress):
        progress.grid(row=ROW_MAXIMUM, column=0, pady=2, columnspan=12, sticky=tk.EW)

    def add_cancel_to_layout(self, btn_cancel):
        btn_cancel.grid(row=ROW_MAXIMUM - 1, column=4, pady=2, columnspan=1)

    def focus_ligand(self, ligand_name):
        if ligand_name != '':
            try:
                ligand = LigandDAO.get_ligand(ligand_name)
                self.parent.highlight_molecule(ligand)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def focus_sbu(self, sbu_name):
        if sbu_name != '':
            try:
                sbu = SBUDAO.get_sbu(sbu_name)
                self.parent.highlight_molecule(sbu)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def regenerate_attribute_row(self):
        self.attribute_row.grid_forget()
        self.attribute_entries = list()
        self.add_attribute_search_entries()

    def clear_previous_results(self):
        self.search_to_results = dict()
        self.redo_search_selected.set('History')
        self.dropdown_redo_search['menu'].delete(0, 'end')

    def reload_ligands(self):
        ligand_names = self.all_ligands_names()
        self.ent_ligand.set_possible_values(ligand_names)
        self.ent_excl_ligand.set_possible_values(ligand_names)

    def reload_sbus(self):
        sbu_names = self.all_sbu_names()
        self.ent_sbus.set_possible_values(sbu_names)
        self.ent_excl_sbus.set_possible_values(sbu_names)


def make_attribute_entry(parent, name, attr):
    if attr.var_type is int or attr.var_type is float:
        return NumericAttributeEntry(parent, name, attr)
    elif attr.var_type is bool:
        return BooleanAttributeEntry(parent, name, attr)
    elif attr.var_type is str:
        return StringAttributeEntry(parent, name, attr)
    else:
        raise Exception(f'Error: {name} is instance of {attr.var_type}, which is not supported.')


class NumericAttributeEntry(tk.Frame):
    def __init__(self, parent, name, attr):
        self.parent = parent
        self.name = name
        tk.Frame.__init__(self, self.parent, bd=1, relief=tk.SOLID)
        self.top = tk.Label(self, text=name)
        Tooltips.create_tool_tip(self.top, attr.description)
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


class StringAttributeEntry(tk.Frame):
    def __init__(self, parent, name, attr):
        self.parent = parent
        self.name = name
        tk.Frame.__init__(self, self.parent, bd=1, relief=tk.SOLID)
        self.top = tk.Label(self, text=name)
        Tooltips.create_tool_tip(self.top, attr.description)
        self.top.grid()
        self.include = tk.Entry(self, width=max(7, len(name)))
        self.include.grid(padx=4)
        self.exclude = tk.Entry(self, width=max(7, len(name)))
        self.exclude.grid(padx=4)

    def get(self):
        if len(self.include.get()) == 0:
            include = None
        else:
            include = self.include.get()
        if len(self.exclude.get()) == 0:
            exclude = None
        else:
            exclude = self.exclude.get()
        return exclude, include


class BooleanAttributeEntry(tk.Frame):
    def __init__(self, parent, name, attr):
        self.parent = parent
        self.name = name
        tk.Frame.__init__(self, self.parent, bd=1, relief=tk.SOLID)
        self.top = tk.Label(self, text=name)
        Tooltips.create_tool_tip(self.top, attr.description)
        self.top.grid()
        self.value = tk.StringVar(self, "-")
        values = {'Either': '-', "Yes": 'Y', "No": 'N'}
        for text, value in values.items():
            ttk.Radiobutton(self, text=text, variable = self.value, value=value).grid()

    def get(self):
        v = self.value.get()
        if v == '-':
            return None
        elif v == 'Y':
            return True
        else:
            return False
