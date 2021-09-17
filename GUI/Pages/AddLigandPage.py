import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilename

from DAO.LigandDatabase import LigandDatabase
from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import LigandView
from DAO import LigandDAO
from MofIdentifier.fileIO import LigandReader

instruction_text = """Choose from your computer a .xyz file or a .smiles file (a plaintext file whose first line is a 
SMILES string) containing information to represent a ligand. The program will calculate which mofs contain the 
ligand, using only atom types and connections (not exact distances nor angles). In order to do so, it must know which 
atoms in the ligand are meant to connect into the larger structure of the MOF and which atoms shouldn't have any 
connections but the ones within the ligand itself. Put a ` symbol (the one above the tab button on most keyboards) 
right after the atomic symbol of any atom that should be open to connecting into the larger structure; the program 
will then allow that to have more bonds and it will require that any atoms not marked as such do not have more bonds; 
see other ligand files for examples. The calculations, which happen as you upload the ligand, will take some time ( 
expect 40-60 minutes), so please be patient. """

instructions_text_2 = """Of note are certain wildcard symbols that can be used in place of element symbols when "
                            "creating ligand input files."""

instructions_text_3 = """For example, you can search for mofs that have water bonded to atoms other than metal by "
                            "requiring a ligand that is a water molecule bonded to a * atom (see the provided "
                            "H2O_bonded.xyz) and excluding a ligand that is a water molecule bonded to a % atom."""

instructions_text_4 = """You can (optionally) put an integer after the wildcard symbol in order to specify the number of
                         other molecules within the ligand to which it should be bonded. For example, the %4 in 
                         M6_node.xyz means that each metal must be bonded to the 4 closest other atoms in the xyz file 
                         (all Oxygen in this case), and may also be bonded to additional atoms outside the xyz file- 
                         connectors, auxililary groups, water, etc."""

"""Of note are certain wildcard symbols that can be used when creating ligand input files."""


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, self.upload_ligand)
        self.mol = None
        self.molecule_v = None
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        tk.Label(self, text=instructions_text_2, justify=tk.LEFT).pack()
        wildcard_instructions_grid = tk.Frame(self)
        tk.Label(wildcard_instructions_grid, text='symbol').grid(sticky=tk.W, row=0, column=0)
        tk.Label(wildcard_instructions_grid, text='use as wildcard').grid(sticky=tk.W, row=0, column=1)
        tk.Label(wildcard_instructions_grid, text='assumed maximum covalent radius').grid(sticky=tk.W, row=0, column=2)
        tk.Label(wildcard_instructions_grid, text='*').grid(sticky=tk.W, row=1, column=0)
        tk.Label(wildcard_instructions_grid, text='matches all atoms').grid(sticky=tk.W, row=1, column=1)
        tk.Label(wildcard_instructions_grid, text='1.7').grid(sticky=tk.W, row=1, column=2)
        tk.Label(wildcard_instructions_grid, text='%').grid(sticky=tk.W, row=2, column=0)
        tk.Label(wildcard_instructions_grid, text='matches metal atoms').grid(sticky=tk.W, row=2, column=1)
        tk.Label(wildcard_instructions_grid, text='1.7').grid(sticky=tk.W, row=2, column=2)
        tk.Label(wildcard_instructions_grid, text='#').grid(sticky=tk.W, row=3, column=0)
        tk.Label(wildcard_instructions_grid, text='matches carbon and hydrogen atoms').grid(sticky=tk.W, row=3, column=1)
        tk.Label(wildcard_instructions_grid, text='1.1').grid(sticky=tk.W, row=3, column=2)
        wildcard_instructions_grid.pack()
        tk.Label(self, text=instructions_text_3, justify=tk.LEFT).pack()
        tk.Label(self, text=instructions_text_4, justify=tk.LEFT).pack()
        btn = StyledButton.make(self, 'Open Ligand', lambda: self.open_file())
        btn.pack()
        self.frm_ligand_preview = tk.Frame(self)
        # LigandView.make_view()
        self.frm_ligand_preview.pack()
        self.add_btn = StyledButton.make(self, 'Add to DB', lambda: self.start_process(self.mol))
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
