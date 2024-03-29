import tkinter as tk
import tkinter.font as tkFont

from DAOsAndServices.AtomSBUMapping import atom_sbu_mapping
from GUI import os_specific_settings, Attributes, Settings
from GUI.Utility import Tooltips
from DAOsAndServices import SBUDAO, LigandDAO, MOFDatabase
from GUI.Utility.HorizontalScrollFrame import HorizontalScrollFrame
from MofIdentifier.fileIO import FileOpen


def select_for_edit(parent, mof):
    parent.winfo_toplevel().select_mof_for_edit(mof)


class View(HorizontalScrollFrame):
    def __init__(self, parent, mof: MOFDatabase.MOFDatabase):
        self.parent = parent
        self.mof = mof
        self.top_page = parent.winfo_toplevel()
        super().__init__(self.parent, height=40, bd=1, relief=tk.SOLID)
        self.frame = self.get_frame()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        name = tk.Label(self.frame, text=mof.filename, width=48, anchor=tk.W)
        name.grid(sticky=tk.W, row=0, column=0)
        self.elements = tk.Label(self.frame, text=mof.atoms_string_with_solvents if Settings.keep_solvent
                            else mof.atoms_string_without_solvents)
        self.elements.grid(row=0, column=1)
        row_icon_btns = tk.Frame(master=self.frame)

        tk.Label(row_icon_btns, text="  ", font=("Arial", 16)).pack(side='left')
        edit = tk.Label(row_icon_btns, text=os_specific_settings.EDIT_ICON, cursor=os_specific_settings.LINK_CURSOR,
                        padx=2, font=("Arial", 16), height=0)
        edit.bind('<Button-1>', lambda e: select_for_edit(parent, mof))
        edit.pack(side='left')

        tk.Label(row_icon_btns, text="  ", font=("Arial", 16)).pack(side='left')
        see = tk.Label(row_icon_btns, text=os_specific_settings.SEE_ICON, cursor=os_specific_settings.LINK_CURSOR,
                       padx=2, font=("Arial", 16), height=0)
        see.bind('<Button-1>', lambda e: FileOpen.make_and_see(mof.get_mof()))
        see.pack(side='left')

        open = tk.Label(row_icon_btns, text=os_specific_settings.OPEN_ICON, cursor=os_specific_settings.LINK_CURSOR,
                        padx=2, font=("Arial", 16), height=0)
        open.bind('<Button-1>', lambda e: FileOpen.make_and_open(mof.get_mof()))
        open.pack(side='left')

        row_icon_btns.grid(sticky=tk.E, row=0, column=2)

        sources = tk.Label(self.frame, text="Sources: " + ", ".join(mof.source_names), width=48, anchor=tk.W)
        sources.grid(sticky=tk.W, row=0, column=3)

        self.attribute_row = self.generate_attribute_row()

        self.generate_sbu_row().grid(sticky=tk.EW, columnspan=4)

        self.generate_ligand_row().grid(sticky=tk.EW, columnspan=4)

    def generate_sbu_row(self):
        sbu_row = tk.Frame(master=self.frame, height=20)
        sbu_label = tk.Label(sbu_row, text=f"{len(self.mof.sbu_names)} SBUs:")
        sbu_label.pack(side='left')
        self.display_sbu_mapping(sbu_row)
        for node in self.mof.sbu_nodes:
            self.display_sbu_name(sbu_row, node, '#0000a0')
        for conn in self.mof.sbu_connectors:
            self.display_sbu_name(sbu_row, conn, '#008100')
        for aux in self.mof.sbu_auxiliaries:
            self.display_sbu_name(sbu_row, aux, '#810000')
        return sbu_row

    def display_sbu_name(self, parent, sbu, color):
        text = f"{sbu.frequency}x {sbu.name} ({sbu.connectivity}*)"
        sbu_label = tk.Label(parent, text=text, fg=color, cursor=os_specific_settings.LINK_CURSOR, padx=3)
        f = tkFont.Font(sbu_label, sbu_label["font"])
        f.configure(underline=True)
        sbu_label.configure(font=f)
        event_function = self.have_page_highlight_sbu(sbu.name)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')

    def display_sbu_mapping(self, parent):
        text = "(view atom-sbu mapping)"
        sbu_label = tk.Label(parent, text=text, cursor=os_specific_settings.LINK_CURSOR, padx=3)
        f = tkFont.Font(sbu_label, sbu_label["font"])
        f.configure(underline=True)
        sbu_label.configure(font=f)
        sbu_label.bind('<Button-1>', lambda _: self.export_and_view_mapping())
        sbu_label.pack(side='left')

    def have_page_highlight_sbu(self, clicked_name):
        def fun(*args):
            sbu = SBUDAO.get_sbu(clicked_name)
            self.top_page.highlight_molecule(sbu)

        return fun

    def generate_ligand_row(self):
        ligand_row = tk.Frame(master=self.frame, height=20)
        ligand_label = tk.Label(ligand_row, text=f"{len(self.mof.ligand_names)} ligands:")
        ligand_label.pack(side='left')
        for name in self.mof.ligand_names:
            self.display_ligand_name(ligand_row, name)
        return ligand_row

    def display_ligand_name(self, parent, name):
        text = name
        ligand_label = tk.Label(parent, text=text, cursor=os_specific_settings.LINK_CURSOR, padx=3)
        f = tkFont.Font(ligand_label, ligand_label["font"])
        f.configure(underline=True)
        ligand_label.configure(font=f)
        event_function = self.have_page_highlight_ligand(name)
        ligand_label.bind('<Button-1>', event_function)
        ligand_label.pack(side='left')

    def have_page_highlight_ligand(self, clicked_name):
        def fun(*args):
            ligand = LigandDAO.get_ligand(clicked_name)
            self.top_page.highlight_molecule(ligand)

        return fun

    def refresh_attributes(self):
        self.attribute_row.grid_forget()
        self.attribute_row = self.generate_attribute_row()

    def refresh_elements(self):
        if self.elements is not None:
            self.elements.grid_forget()
        self.elements = tk.Label(self.frame, text=self.mof.atoms_string_with_solvents if Settings.keep_solvent
                                 else self.mof.atoms_string_without_solvents)
        self.elements.grid(row=0, column=1)

    def generate_attribute_row(self):
        row = tk.Frame(master=self.frame, height=20)
        i = 0
        for text, attr in Attributes.attributes.items():
            if Settings.attribute_is_enabled[text]:
                val = attr.calculate(self.mof)
                if attr.var_type is bool and val is not None:
                    val = "True" if val else "False"
                _attribute_view(row, text, val, attr.description).grid(column=i, row=0, sticky=tk.EW)
                row.grid_columnconfigure(i, weight=1)
                i += 1
        row.grid(sticky=tk.EW, row=1, columnspan=4)
        return row

    def export_and_view_mapping(self):
        FileOpen.make_and_see_text(atom_sbu_mapping(self.mof), f"{self.mof.filename}_atom_sbu_mapping.csv")


def _attribute_view(parent, name, value, description):
    view = tk.Frame(parent, bd=0, relief=tk.SOLID)
    view.config(highlightbackground=os_specific_settings.secondary_color,
                highlightcolor=os_specific_settings.secondary_color, highlightthickness=1)
    top = tk.Label(view, text=name)
    Tooltips.create_tool_tip(top, description)
    top.pack()
    bottom = tk.Label(view, text=value)
    bottom.pack()
    return view
