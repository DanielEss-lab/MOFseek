import tkinter as tk
from tkinter.filedialog import askopenfilename

from MofIdentifier.fileIO import CifReader, LigandReader


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, bd=2, relief=tk.SOLID)

        btn = tk.Button(self, text='Open Ligand', command=lambda: self.open_file())
        btn.pack()

    def open_file(self):
        file = askopenfilename(filetypes=[('XYZ Files', '*.xyz'), ('SMILES Files', '*.txt')])
        if file is not None:
            mol = LigandReader.get_mol_from_file(file)
            print(mol)