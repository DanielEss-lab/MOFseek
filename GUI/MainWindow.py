import tkinter as tk
import tkinter.ttk as ttk

from GUI import os_specific_settings
from GUI.Pages import SearchPage, AddLigandPage, AddMofPage, RenameSBUPage, RenameLigandPage, EditMOFPage, SettingsPage


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Ess lab | P66 | GUI WIP")

        self.geometry('1100x900')
        self.minsize(720, 500)
        self.set_styles()

        self.tabControl = ttk.Notebook(self)
        self.tabControl.bind('<<NotebookTabChanged>>', self.on_tab_change)
        self.prev_tab_name = ''

        self.search_page = SearchPage.SearchPage(self.tabControl)
        self.add_ligand_page = AddLigandPage.AddLigandPage(self.tabControl)
        self.rename_ligand_page = RenameLigandPage.Page(self.tabControl)
        self.rename_sbu_page = RenameSBUPage.Page(self.tabControl)
        self.add_MOFs_page = AddMofPage.Page(self.tabControl)
        self.edit_MOF_page = EditMOFPage.Page(self.tabControl)
        self.settings_page = SettingsPage.Page(self.tabControl)

        self.tabControl.add(self.search_page, text='Search')
        self.tabControl.add(self.add_ligand_page, text='Add Ligand')
        self.tabControl.add(self.rename_ligand_page, text='Rename Ligand')
        self.tabControl.add(self.rename_sbu_page, text='Rename SBU')
        self.tabControl.add(self.add_MOFs_page, text='Add MOFs')
        self.tabControl.add(self.edit_MOF_page, text='Edit MOF')
        self.tabControl.add(self.settings_page, text='Settings')
        self.tabControl.pack(expand=1, fill="both")

    def on_tab_change(self, event):
        if self.prev_tab_name == 'Settings':
            self.display_attributes_by_settings()
        self.prev_tab_name = event.widget.tab('current')['text']

    def select_mof_for_edit(self, mof):
        if self.tabControl.index('current') != 5:
            self.edit_MOF_page.select_mof(mof)
            self.tabControl.select(5)

    def select_ligand_for_edit(self, ligand):
        self.rename_ligand_page.select_ligand(ligand)
        self.tabControl.select(2)

    def select_sbu_for_edit(self, sbu):
        self.rename_sbu_page.select_sbu(sbu)
        self.tabControl.select(3)

    def set_styles(self):
        s = ttk.Style()
        print(s.theme_names())
        s.configure("TMenubutton", background="#ffffff")
        s.configure("TMenubutton", background="#ffffff")
        s.configure("my.button", font=('Arial', 16))
        os_specific_settings.style_for_platform(s)

    def add_custom_ligand(self, mol):  # To change when connecting to DB
        self.search_page.search_v.add_custom_ligand(mol)
        self.rename_ligand_page.add_custom_ligand(mol)

    def highlight_molecule(self, mol):
        self.search_page.highlight_molecule(mol)
        self.tabControl.select(0)

    def display_attributes_by_settings(self):
        self.search_page.refresh_attributes_shown()
        self.add_MOFs_page.refresh_attributes_shown()
        self.edit_MOF_page.refresh_attributes_shown()

    def force_search_ligand(self, molecule):
        self.search_page.search_v.force_search_ligand(molecule)

    def force_search_sbu(self, molecule):
        self.search_page.search_v.force_search_sbu(molecule)

    def toggle_sbu_search(self, enabled):
        if enabled:
            self.search_page.show_sbu_search()
        else:
            self.search_page.hide_sbu_search()
