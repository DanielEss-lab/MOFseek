import tkinter as tk
from pathlib import Path

from GUI.Views import MoleculeView, SBUView
from GUI.Utility import AutoCompleteComboBox, FrameWithProcess
from MofIdentifier.DAO import SBUDAO
from MofIdentifier.fileIO import LigandReader
from MofIdentifier.subbuilding import SBUCollectionManager

instruction_text = """Renaming a Secondary Building Unit in the database takes several minutes, so please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.custom_sbus = dict()
        super().__init__(self.parent, lambda new_name: self.rename(new_name))
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.combobox = AutoCompleteComboBox.Box(self, ("Arial", 10), self.focus_sbu)
        self.combobox.pack()
        self.values = self.all_sbu_names()
        self.combobox.set_completion_list(self.values)
        self.combobox.focus_set()
        self.molecule_v = None
        row1 = tk.Frame(self)
        self.new_name_ent = tk.Entry(row1)
        self.new_name_ent.pack(side=tk.LEFT)
        self.extension_text = tk.Label(row1, text='.xyz')
        self.extension_text.pack(side=tk.LEFT)
        row1.pack()
        self.rename_button = tk.Button(self, text="Rename", command=lambda: self.start_process(self.new_name_ent.get()))
        self.rename_button.pack()
        self.mol = None

    def rename(self, new_name):
        if self.mol is not None and self.mol.label == self.combobox.get():
            if new_name != '':
                if new_name.find(' ') < 0 and new_name.find('.') < 0:
                    self.combobox.set('')
                    self.new_name_ent.delete(0, tk.END)
                    new_name = new_name + self.extension_text['text']
                    SBUDAO.rename_sbu(self.mol.label, new_name)
                    pass
                else:
                    self._show_error('Name cannot contain a period or a space')
            else:
                self._show_error('Cannot rename to an empty string')
        else:
            self._show_error('Name in selection box does not match a valid molecule')

    def focus_sbu(self, sbu_name):
        if sbu_name != '':
            try:
                mol = self.get_sbus([sbu_name])[0]
                self.set_mol_in_view(mol)
            except FileNotFoundError as ex:
                self._show_error(ex)

    def all_sbu_names(self):  # Will change with adding DB
        path_1 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/cluster")
        path_2 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/connector")
        path_3 = str(Path(__file__).parent / "../../MofIdentifier/subbuilding/auxiliary")
        sbus = LigandReader.get_all_mols_from_directory(path_1) + \
               LigandReader.get_all_mols_from_directory(path_2) + \
               LigandReader.get_all_mols_from_directory(path_3)
        return [sbu.label for sbu in sbus]

    def get_sbus(self, sbu_names):
        sbus = list()
        other_sbus = list()
        for sbu_name in sbu_names:
            if sbu_name in self.custom_sbus:
                sbus.append(self.custom_sbus[sbu_name])
            else:
                other_sbus.append(sbu_name)
        sbus.extend(SBUCollectionManager.read_sbus_from_files(other_sbus))
        return sbus

    def select_sbu(self, sbu):
        self.set_mol_in_view(sbu)
        self.combobox.set(sbu.label)

    def set_mol_in_view(self, mol):
        self.mol = mol
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = SBUView.View(self, self.mol)
        self.molecule_v.pack(side=tk.BOTTOM)
