import tkinter as tk

from GUI import os_specific_settings
from MofIdentifier.DAO.LigandDatabase import LigandDatabase
from MofIdentifier.fileIO import FileOpen
import tkinter.font as tkFont


def select_for_edit(parent, ligand):
    parent.winfo_toplevel().select_ligand_for_edit(ligand)


class View(tk.Frame):
    def __init__(self, parent, ligand: LigandDatabase):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=40, width=120, bd=1, relief=tk.SOLID)
        self.ligand = ligand
        self.top_page = parent.winfo_toplevel()

        row1 = tk.Frame(master=self)
        name = tk.Label(row1, text=ligand.name)
        name.pack(side='left')
        open = tk.Label(row1, text=os_specific_settings.OPEN_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
        open.bind('<Button-1>', lambda e: FileOpen.make_and_open(ligand))
        open.pack(side='right')
        tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
        see = tk.Label(row1, text=os_specific_settings.SEE_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
        see.bind('<Button-1>', lambda e: FileOpen.make_and_see(ligand))
        see.pack(side='right')
        tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
        edit = tk.Label(row1, text=os_specific_settings.EDIT_ICON, cursor=os_specific_settings.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
        edit.bind('<Button-1>', lambda e: select_for_edit(parent, ligand))
        edit.pack(side='right')
        search = tk.Label(row1, text="Search as SBU", cursor=os_specific_settings.LINK_CURSOR, padx=8)
        f = tkFont.Font(search, search["font"])
        f.configure(underline=True)
        search.configure(font=f)
        search.bind('<Button-1>', lambda e: parent.winfo_toplevel().force_search_sbu(ligand))
        search.pack(side='right')
        sbu_search = tk.Label(row1, text="Search", cursor=os_specific_settings.LINK_CURSOR, padx=8)
        f = tkFont.Font(sbu_search, sbu_search["font"])
        f.configure(underline=True)
        sbu_search.configure(font=f)
        sbu_search.bind('<Button-1>', lambda e: parent.winfo_toplevel().force_search_ligand(ligand))
        sbu_search.pack(side='right')
        row1.pack(fill=tk.X)

        row2 = tk.Frame(master=self)
        file_first_line = ligand.file_content.partition('\n')[0]
        first_line_label = tk.Label(row2, text=file_first_line)
        first_line_label.pack(side=tk.RIGHT)
        elements = tk.Label(row2, text=ligand.get_ligand().atoms_string())
        elements.pack(side=tk.LEFT)
        row2.pack(fill=tk.X)

        row3 = tk.Frame(master=self, height=20)
        mof_label = tk.Label(row3, text=f"In {len(ligand.Mofs)} MOFs: {ligand.Mofs}", wraplength=parent.winfo_width(), justify=tk.LEFT)
        # mof_label.bind('<Configure>', lambda _: self.config(wraplength=self.winfo_width()))
        mof_label.pack(side='left')
        row3.pack(fill=tk.X)
