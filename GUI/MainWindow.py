import tkinter as tk
import tkinter.ttk as ttk

from GUI import SearchResultsView, MoleculeView
from GUI.Search import SearchView


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Ess lab | P66 | GUI WIP")

        self.geometry('1100x900')
        self.set_styles()

        self.search_v = SearchView.View(self)
        self.search_v.pack()
        self.search_results_v = SearchResultsView.View(self)
        self.search_results_v.pack(fill=tk.X)

        self.molecule_v = None

    def display_search_results(self, results):
        self.search_results_v.display_results(results)

    def set_styles(self):
        s = ttk.Style()
        s.configure("TMenubutton", background="#ffffff")

    def highlight_molecule(self, mol):
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, mol)
        self.molecule_v.pack(side=tk.BOTTOM)
