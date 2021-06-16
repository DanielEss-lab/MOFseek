import tkinter as tk
from pathlib import Path

from GUI.Views import MoleculeView
from GUI.Utility import AutoCompleteComboBox, FrameWithProcess
from MofIdentifier import SearchMOF
from MofIdentifier.fileIO import LigandReader

instruction_text = """Renaming a ligand in the database takes several minutes, so please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.custom_ligands = dict()
        super().__init__(self.parent, lambda new_name: self.rename(new_name))
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.combobox = AutoCompleteComboBox.Box(self, ("Arial", 10), self.focus_ligand)
        self.combobox.pack()
        self.values = self.all_ligands_names()
        self.combobox.set_completion_list(self.values)
        self.combobox.focus_set()
        self.molecule_v = None
        row1 = tk.Frame(self)
        self.new_name_ent = tk.Entry(row1)
        self.new_name_ent.pack(side=tk.LEFT)
        self.extension_text = tk.Label(row1, text='')
        self.extension_text.pack(side=tk.LEFT)
        row1.pack()
        self.rename_button = tk.Button(self, text="Rename", command=lambda: self.start_process(self.new_name_ent.get()))
        self.rename_button.pack()
        self.mol = None

    def rename(self, new_name):
        if self.mol is not None and self.mol.label == self.combobox.get():
            if new_name != '':
                if new_name.find(' ') < 0 and new_name.find('.') < 0:
                    new_name = new_name + self.extension_text['text']
                    # TODO: link to DAO
                    pass
                else:
                    self._show_error('Name cannot contain a period or a space')
            else:
                self._show_error('Cannot rename to an empty string')
        else:
            self._show_error('Name in selection box does not match a valid molecule')

    def focus_ligand(self, ligand_name):
        if ligand_name != '':
            try:
                mol = self.get_ligands([ligand_name])[0]
                self.set_mol_in_view(mol)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def all_ligands_names(self):  # Will change with adding DB
        path = str(Path(__file__).parent / "../../MofIdentifier/ligands")
        ligands = LigandReader.get_all_mols_from_directory(path)
        return [ligand.label for ligand in ligands]

    def get_ligands(self, ligand_names):
        ligands = list()
        other_ligands = list()
        for ligand_name in ligand_names:
            if ligand_name in self.custom_ligands:
                ligands.append(self.custom_ligands[ligand_name])
            else:
                other_ligands.append(ligand_name)
        ligands.extend(SearchMOF.read_ligands_from_files(other_ligands))
        return ligands

    def add_custom_ligand(self, mol):
        self.values.append('* ' + mol.label)
        self.combobox.set_completion_list(self.values)
        self.custom_ligands['* ' + mol.label] = mol

    def select_ligand(self, ligand):
        self.set_mol_in_view(ligand)
        self.combobox.set(ligand.label)

    def set_mol_in_view(self, mol):
        self.mol = mol
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, self.mol)
        self.extension_text.config(text='.' + self.mol.label[-3:])
        self.molecule_v.pack(side=tk.BOTTOM)
