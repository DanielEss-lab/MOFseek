import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from MofIdentifier.fileIO import LigandReader


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)

        btn = tk.Button(self, text='Open Ligand', command=lambda: self.open_file())
        btn.pack()

    def open_file(self):
        filename = askopenfilename(filetypes=[('XYZ Files', '*.xyz'), ('SMILES Files', '*.txt')])
        if filename is not None and len(filename) > 0:
            try:
                mol = LigandReader.get_mol_from_file(str(Path(filename)))
            except:
                messagebox.showerror("Bad File", "Unable to extract a molecule from this file")
                return
            self.parent.start_process(mol)
