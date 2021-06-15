import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

from GUI.Utility import FrameWithProcess
from GUI.Views import LigandView
from MofIdentifier.fileIO import LigandReader

instruction_text = """Choose from your computer a .xyz file or a .txt file whose first line is a SMILES string. It will 
be loaded onto the database and added to the ligand list of all MOFs that contain it. The calculations will take some 
time (expect 20-60 minutes), so please be patient."""


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, self.upload_ligand)
        self.mol = None
        self.molecule_v = None
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        btn = tk.Button(self, text='Open Ligand', command=lambda: self.open_file())
        btn.pack()
        self.frm_ligand_preview = tk.Frame(self)
        # LigandView.make_view()
        self.frm_ligand_preview.pack()
        self.add_btn = tk.Button(self, text='Upload to DB', command=lambda: self.start_process(self.mol))
        self.add_btn['state'] = "disabled"
        self.add_btn.pack()

    def upload_ligand(self, mol):
        self.add_btn['state'] = "disabled"
        self.mol = None
        self.molecule_v.destroy()
        if self.mol is not None:
            self.winfo_toplevel().add_custom_ligand(mol)  # TODO: hook up to DB

    def open_file(self):
        filename = askopenfilename(filetypes=[('XYZ Files', '*.xyz'), ('SMILES Files', '*.txt')])
        if filename is not None and len(filename) > 0:
            if self.molecule_v is not None:
                self.molecule_v.destroy()
            try:
                self.mol = LigandReader.get_mol_from_file(str(Path(filename)))
                self.molecule_v = LigandView.make_view(self.frm_ligand_preview, self.mol)
                self.add_btn['state'] = "normal"
                self.molecule_v.pack()
            except:
                self._show_error("Unable to extract a molecule from this file")
                return
