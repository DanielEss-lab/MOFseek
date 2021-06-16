import tkinter as tk
import tkinter.ttk as ttk

from GUI.Pages import SearchPage, AddLigandPage, AddMofPage, RenameSBUPage, RenameLigandPage, EditMOFPage


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Ess lab | P66 | GUI WIP")

        self.geometry('1100x900')
        self.minsize(1050, 500)
        self.set_styles()

        self.tabControl = ttk.Notebook(self)

        self.search_page = SearchPage.SearchPage(self.tabControl)
        self.add_ligand_page = AddLigandPage.AddLigandPage(self.tabControl)
        self.rename_ligand_page = RenameLigandPage.Page(self.tabControl)
        self.rename_sbu_page = RenameSBUPage.Page(self.tabControl)
        self.add_MOFs = AddMofPage.Page(self.tabControl)
        self.edit_MOF = EditMOFPage.Page(self.tabControl)

        self.tabControl.add(self.search_page, text='Search')
        self.tabControl.add(self.add_ligand_page, text='Add Ligand')
        self.tabControl.add(self.rename_ligand_page, text='Rename Ligand')
        self.tabControl.add(self.rename_sbu_page, text='Rename SBU')
        self.tabControl.add(self.add_MOFs, text='Add MOFs')
        self.tabControl.add(self.edit_MOF, text='Edit MOF')
        self.tabControl.pack(expand=1, fill="both")

    def select_mof_for_edit(self, mof):
        self.edit_MOF.select_mof(mof)
        self.tabControl.select(5)

    def select_ligand_for_edit(self, ligand):
        self.rename_ligand_page.select_ligand(ligand)
        self.tabControl.select(2)

    def select_sbu_for_edit(self, sbu):
        self.rename_sbu_page.select_sbu(sbu)
        self.tabControl.select(3)

    def set_styles(self):
        s = ttk.Style()
        s.configure("TMenubutton", background="#ffffff")

    def add_custom_ligand(self, mol):  # To change when connecting to DB
        self.search_page.search_v.add_custom_ligand(mol)
        self.rename_ligand_page.add_custom_ligand(mol)
