import tkinter as tk

from GUI.Utility.ScrollFrame import ScrollFrame
from GUI.Views import LigandView


class View(ScrollFrame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, height=450)
        self.results = []

        self.ligands_frame = super().get_frame()
        self.ligands_frame.grid_columnconfigure(0, weight=1)

    def display_results(self, results):
        self.results = results
        for widget in self.ligands_frame.winfo_children():
            widget.destroy()
        self.ligands_frame.focus_set()
        self.canvas.yview_moveto(0)
        num_shown = 0
        for ligand in results:
            ligand_v = LigandView.View(self.ligands_frame, ligand)
            ligand_v.grid(sticky=tk.EW)
            num_shown += 1
            if num_shown >= 100:
                break
