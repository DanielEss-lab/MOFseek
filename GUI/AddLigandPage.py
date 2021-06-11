import tkinter as tk

from GUI import UploadLigandView, FrameWithProcess

instruction_text = """Choose from your computer a .xyz file or a .txt file whose first line is a SMILES string. It will 
be loaded onto the database and added to the ligand list of all MOFs that contain it. The calculations will take some 
time (expect 20-60 minutes), so please be patient."""


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda mol: self.winfo_toplevel().add_custom_ligand(mol))  # Does it pass self?
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.upload_ligand_v = UploadLigandView.View(self)
        self.upload_ligand_v.pack()
