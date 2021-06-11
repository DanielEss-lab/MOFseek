import tkinter as tk
import tkinter.ttk as ttk

from GUI import SearchPage, AddLigandPage


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Ess lab | P66 | GUI WIP")

        self.geometry('1100x900')
        self.set_styles()

        self.tabControl = ttk.Notebook(self)

        self.search_page = SearchPage.SearchPage(self.tabControl)
        self.add_ligand_page = AddLigandPage.AddLigandPage(self.tabControl)
        self.rename_ligand_page = ttk.Frame(self.tabControl)  # Todo
        self.rename_sbu_page = ttk.Frame(self.tabControl)  # Todo
        self.add_MOFs = ttk.Frame(self.tabControl)  # Todo
        self.edit_MOF = ttk.Frame(self.tabControl)  # Todo

        self.tabControl.add(self.search_page, text='Search')
        self.tabControl.add(self.add_ligand_page, text='Add Ligand')
        self.tabControl.add(self.rename_ligand_page, text='Rename Ligand')
        self.tabControl.add(self.rename_sbu_page, text='Rename SBU')
        self.tabControl.add(self.add_MOFs, text='Add MOFs')
        self.tabControl.add(self.edit_MOF, text='Edit MOF')
        self.tabControl.pack(expand=1, fill="both")


    def set_styles(self):
        s = ttk.Style()
        s.configure("TMenubutton", background="#ffffff")

    def add_custom_ligand(self, mol):  # To change when connecting to DB
        self.search_page.search_v.add_custom_ligand(mol)
