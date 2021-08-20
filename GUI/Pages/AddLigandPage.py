import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilename

from DAO.LigandDatabase import LigandDatabase
from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import LigandView
from DAO import LigandDAO
from MofIdentifier.fileIO import LigandReader

instruction_text = """Choose from your computer a .xyz file or a .smiles plaintext file whose first line 
is a SMILES string. It will be loaded onto the database and added to the ligand list of all MOFs that 
contain it. The calculations will take some time (expect 40-60 minutes), so please be patient."""


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, self.upload_ligand)
        self.mol = None
        self.molecule_v = None
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        btn = StyledButton.make(self, 'Open Ligand', lambda: self.open_file())
        btn.pack()
        self.frm_ligand_preview = tk.Frame(self)
        # LigandView.make_view()
        self.frm_ligand_preview.pack()
        self.add_btn = StyledButton.make(self, 'Upload to DB', lambda: self.start_process(self.mol))
        self.add_btn['state'] = "disabled"
        self.add_btn.pack()

    def upload_ligand(self, mol):
        self.add_btn['state'] = "disabled"
        self.molecule_v.destroy()
        if mol is not None:
            LigandDAO.add_ligand_to_db(mol)
            print('done')
            self.winfo_toplevel().reload_ligands()
        self.mol_for_db = None

    def open_file(self):
        filename = askopenfilename(filetypes=[('XYZ Files', '*.xyz'), ('SMILES Files', '*.smiles')])
        if filename is not None and len(filename) > 0:
            if self.molecule_v is not None:
                self.molecule_v.destroy()
            try:
                self.mol = LigandReader.get_mol_from_file(str(Path(filename)))
                fake_db_mol = LigandDatabase(self.mol.label, self.mol.file_content, [])
                self.molecule_v = LigandView.View(self.frm_ligand_preview, fake_db_mol)
                self.add_btn['state'] = "normal"
                self.molecule_v.pack()
            except:
                self._show_error("Unable to extract a molecule from this file")
                return
