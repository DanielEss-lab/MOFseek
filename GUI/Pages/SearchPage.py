import platform
import tkinter as tk

from GUI import Settings
from GUI.Pages.Search import SearchView, SearchResultsView
from GUI.Views import MoleculeView


class SearchPage(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)

        self.search_v = SearchView.View(self)
        self.search_v.pack()
        self.search_results_v = SearchResultsView.View(self)
        self.search_results_v.pack(fill=tk.BOTH, expand=True)
        if Settings.use_sbu_search:
            self.show_sbu_search()
        self.molecule_v = None

    def highlight_molecule(self, mol):
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, mol)
        self.molecule_v.pack(side=tk.BOTTOM)

    def refesh_mol_views(self):
        if self.molecule_v is not None:
            self.highlight_molecule(self.molecule_v.mol)

    def display_search_results(self, results):
        self.search_results_v.start_process(results)

    def refresh_elements_shown(self):
        self.search_results_v.main_body.refresh_all_elements()

    def refresh_attributes_shown(self):
        self.search_results_v.main_body.refresh_all_attributes()
        self.search_results_v.rebuild_sort_dropdown()
        self.search_v.regenerate_attribute_row()

    def show_sbu_search(self):
        self.search_v.lbl_sbus.grid(row=1, column=4, pady=2, sticky=tk.NE)
        self.search_v.ent_sbus.grid(row=1, column=5, pady=2, sticky=tk.EW)
        self.search_v.lbl_excl_sbus.grid(row=2, column=4, pady=2, sticky=tk.NE)
        self.search_v.ent_excl_sbus.grid(row=2, column=5, pady=2, sticky=tk.W)

    def hide_sbu_search(self):
        self.search_v.lbl_sbus.grid_forget()
        self.search_v.ent_sbus.grid_forget()
        self.search_v.lbl_excl_sbus.grid_forget()
        self.search_v.ent_excl_sbus.grid_forget()
        self.search_v.ent_sbus.clear()
        self.search_v.ent_excl_sbus.clear()

    def forget_history(self):
        self.search_v.clear_previous_results()

    def reload_ligands(self):
        self.search_v.reload_ligands()

    def reload_sbus(self):
        self.search_v.reload_sbus()
