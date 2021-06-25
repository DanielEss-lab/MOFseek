import tkinter as tk

from GUI.Views import MoleculeView
from GUI.Search import SearchView, SearchResultsView


class SearchPage(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)

        self.search_v = SearchView.View(self)
        self.search_v.pack()
        self.search_results_v = SearchResultsView.View(self)
        self.search_results_v.pack(fill=tk.BOTH, expand=True)

        self.molecule_v = None

    def highlight_molecule(self, mol):
        # Splitting this into two methods (one for sbus, one for ligands)
        # shouldn't be necessary once the DB is hooked up, so I won't do it now
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, mol)
        self.molecule_v.pack(side=tk.BOTTOM)

    def display_search_results(self, results):
        self.search_results_v.start_process(results)

    def refresh_attributes_shown(self):
        self.search_results_v.main_body.refresh_all_attributes()
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