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
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, mol)
        self.molecule_v.pack(side=tk.BOTTOM)

    def display_search_results(self, results):
        self.search_results_v.start_process(results)