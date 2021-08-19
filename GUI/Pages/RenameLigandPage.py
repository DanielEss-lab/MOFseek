import tkinter as tk

from GUI.Views import MoleculeView
from GUI.Utility import AutoCompleteComboBox, FrameWithProcess, StyledButton
from DAO import LigandDAO, RenameService

instruction_text = """Renaming a ligand in the database takes several minutes, so please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
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
        self.rename_button = StyledButton.make(self, text="Rename",
                                               command=lambda: self.start_process(self.new_name_ent.get()))
        self.rename_button.pack()
        self.mol = None

    def rename(self, new_name):
        if self.mol is not None and self.mol.ligand_name == self.combobox.get():
            if new_name != '':
                if new_name.find(' ') < 0 and new_name.find('.') < 0:
                    self.combobox.set('')
                    self.new_name_ent.delete(0, tk.END)
                    new_name = new_name + self.extension_text['text']
                    RenameService.rename_ligand(self.mol.ligand_name, new_name)
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
                mol = LigandDAO.get_ligand(ligand_name)
                self.set_mol_in_view(mol)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def all_ligands_names(self):
        return LigandDAO.get_all_names()

    def select_ligand(self, ligand):
        self.set_mol_in_view(ligand)
        self.combobox.set(ligand.ligand_name)

    def set_mol_in_view(self, mol):
        self.mol = mol
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, self.mol)
        extension_text = mol.ligand_name[mol.ligand_name.rindex('.'):]
        self.extension_text.config(text=extension_text)
        self.molecule_v.pack(side=tk.BOTTOM)
