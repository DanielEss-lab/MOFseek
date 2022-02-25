import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilenames

from DAOsAndServices.LigandDatabase import LigandDatabase
from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import LigandView, MultiLigandView
from DAOsAndServices import LigandDAO
from MofIdentifier.fileIO import LigandReader

instruction_text = """Choose from your computer a .xyz file or a .smiles file (a plaintext file whose first line is a
SMILES string) containing information to represent a ligand. The program will calculate which mofs contain the 
ligand, using only atom types and connections (not exact distances nor angles). In order to do so, it must know which 
atoms in the ligand are meant to connect into the larger structure of the MOF and which atoms shouldn't have any 
connections other than the ones within the ligand itself. Put a ` symbol (the one above the tab button on most 
keyboards) right after the atomic symbol of any atom that should be open to connecting into the larger structure; the 
program will then allow that marked symbols may have more bonds, and it will require that any atoms not marked as 
such do not have more bonds; see other ligand files for examples. The calculations, which happen as you upload the 
ligand, will take some time (expect 40-80 minutes per ligand), so please be patient."""

instructions_text_2 = """To allow some flexibility in defining ligands, wildcards are allowed. We provide three 
wildcards (* to match anything, & to match metals, and ~ to match C and H only), and you can use the following format 
in the second line of the file in order to define custom wildcards for your own use:<br><t>Wca = <comma separated 
list of atomic symbols><br>Or, if it should match most elements with certain exceptions:<br><t>Wca = not <comma 
separated list of atomic symbols><br>You can define multiple wildcards separated by semicolons, using Wca, Wcb, Wcc, 
Wcd, etc. for the wildcard symbols. For example, a line may look like:<br><t>Wca=V,Nb,Ta,Db; Wcb=not H<br>Spaces and 
tabs are ignored. """

instructions_text_3 = """Wildcards in xyz files are usually correct, but an unknown atom has an unknown bond radius, 
so sometimes the program has difficulty knowing which atoms it should be bonded to. For this reason, using smiles is 
recommended for complex ligands involving wildcards."""


def line_correct(text):
    text = ' '.join(text.split())
    text = text.replace('<br>', '\n')
    text = text.replace('<t>', '\t')
    return text


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, self.upload_ligand)
        self.ligands = []
        self.label_of(instruction_text).pack()
        self.label_of(instructions_text_2).pack()
        self.label_of(instructions_text_3).pack()
        btn = StyledButton.make(self, 'Choose ligand(s)', lambda: self.open_files())
        btn.pack()
        self.ligand_preview = MultiLigandView.View(self)
        self.ligand_preview.pack()
        self.add_btn = StyledButton.make(self, 'Add to DB', lambda: self.start_process(self.ligands))
        self.add_btn['state'] = "disabled"
        self.add_btn.pack()

    def upload_ligand(self, ligands):
        self.add_btn['state'] = "disabled"
        if len(self.ligands) > 0:
            for ligand in ligands:
                LigandDAO.add_ligand_to_db(ligand)
            self.winfo_toplevel().reload_ligands()
        self.ligands = []

    def open_files(self):
        filenames = askopenfilenames(filetypes=[('XYZ Files', '*.xyz'), ('SMILES Files', '*.smiles')])
        if filenames is not None and len(filenames) > 0:
            self.ligands = []
            ligands_for_display = []
            for filename in filenames:
                try:
                    ligand = LigandReader.get_mol_from_file(str(Path(filename)))
                    if any(not atom.is_bond_limited for atom in ligand.atoms):
                        self.ligands.append(ligand)
                        ligands_for_display.append(LigandDatabase(ligand.label, ligand.file_content, []))
                    else:
                        self._show_error(f'Ligand {filename} has no backticks and therefore will not match any MOFs.')
                except:
                    self._show_error('Unable to extract molecule from ' + filename)

            self.ligand_preview.display_results(ligands_for_display)
            if len(ligands_for_display) > 0:
                self.add_btn['state'] = "normal"

    def label_of(self, text):
        l = tk.Label(self, text=line_correct(text), justify=tk.LEFT, width=100, anchor=tk.W, pady=8)
        l.bind("<Configure>", self.set_label_wrap)
        return l

    def set_label_wrap(self, event):
        wraplength = event.width - 8
        event.widget.configure(wraplength=wraplength)

