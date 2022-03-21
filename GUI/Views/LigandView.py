import tkinter as tk
import tkinter.font as tkFont

from GUI import os_specific_settings, Settings
from DAOsAndServices import MOFDAO
from DAOsAndServices.LigandDatabase import LigandDatabase
from GUI.SourceCheck import mof_source_is_enabled
from MofIdentifier.fileIO import FileOpen


def select_for_edit(parent, ligand):
    parent.winfo_toplevel().select_ligand_for_edit(ligand)


class View(tk.Frame):
    def __init__(self, parent, ligand: LigandDatabase):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=40, width=120, bd=1, relief=tk.SOLID)
        self.mol = ligand
        self.top_page = parent.winfo_toplevel()

        row1 = tk.Frame(master=self)
        name = tk.Label(row1, text=ligand.name)
        name.pack(side='left')
        open = tk.Label(row1, text=os_specific_settings.OPEN_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
        open.bind('<Button-1>', lambda e: FileOpen.make_and_open(ligand.get_ligand()))
        open.pack(side='right')
        tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
        see = tk.Label(row1, text=os_specific_settings.SEE_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
        see.bind('<Button-1>', lambda e: FileOpen.make_and_see(ligand.get_ligand()))
        see.pack(side='right')
        tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
        edit = tk.Label(row1, text=os_specific_settings.EDIT_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
        edit.bind('<Button-1>', lambda e: select_for_edit(parent, ligand))
        edit.pack(side='right')
        search = tk.Label(row1, text="Search", cursor=os_specific_settings.LINK_CURSOR, padx=8)
        f = tkFont.Font(search, search["font"])
        f.configure(underline=True)
        search.configure(font=f)
        search.bind('<Button-1>', lambda e: parent.winfo_toplevel().force_search_ligand(ligand.name))
        search.pack(side='right')
        row1.pack(fill=tk.X)

        row2 = tk.Frame(master=self)
        file_first_line = ligand.file_content.partition('\n')[0]
        first_line_label = tk.Label(row2, text=file_first_line)
        first_line_label.pack(side=tk.RIGHT)
        elements = tk.Label(row2, text=ligand.get_ligand().atoms_string())
        elements.pack(side=tk.LEFT)
        row2.pack(fill=tk.X)

        self.generate_mof_row().pack(fill=tk.X)

    def generate_mof_row(self):
        mof_row = tk.Frame(master=self, height=20)
        if all(Settings.current_source_states().values()):
            mofs = self.mol.Mofs
        else:
            mofs = (name for name in self.mol.Mofs if mof_source_is_enabled(name))
        mof_label = tk.Label(mof_row, text=f"{len(mofs)} MOFs: ")
        mof_label.pack(side='left')
        for name in mofs:
            self.display_mof_name(mof_row, name)
        return mof_row

    def display_mof_name(self, parent, name):
        text = name
        mof_label = tk.Label(parent, text=text, cursor=os_specific_settings.LINK_CURSOR, padx=3)
        f = tkFont.Font(mof_label, mof_label["font"])
        f.configure(underline=True)
        mof_label.configure(font=f)
        event_function = self.have_page_highlight_mof(name)
        mof_label.bind('<Button-1>', event_function)
        mof_label.pack(side='left')

    def have_page_highlight_mof(self, clicked_name):
        def fun(*args):
            mof = MOFDAO.get_MOF(clicked_name)
            self.top_page.highlight_molecule(mof)

        return fun
