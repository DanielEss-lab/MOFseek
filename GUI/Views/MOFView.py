import tkinter as tk
import tkinter.font as tkFont

from GUI import icons
from GUI.Utility import Tooltips
from GUI.Search import Attributes
from MofIdentifier.fileIO import FileOpen
from MofIdentifier.subbuilding import SBUCollectionManager


def select_for_edit(parent, mof):
    parent.winfo_toplevel().select_mof_for_edit(mof)


class View(tk.Frame):
    def __init__(self, parent, mof):
        self.parent = parent
        self.mof = mof
        self.top_page = parent.winfo_toplevel()
        tk.Frame.__init__(self, self.parent, height=40, bd=1, relief=tk.SOLID)
        self.sbus = SBUCollectionManager.process_new_mof(mof)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        name = tk.Label(self, text=mof.label, width=48, anchor=tk.W)
        name.grid(sticky=tk.W, row=0, column=0)
        elements = tk.Label(self, text=mof.atoms_string())
        elements.grid(row=0, column=1)
        row_icon_btns = tk.Frame(master=self)
        open = tk.Label(row_icon_btns, text=icons.OPEN_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
        open.bind('<Button-1>', lambda e: FileOpen.open_file(mof.filepath))
        open.pack(side='right')
        tk.Label(row_icon_btns, text="  ", font=("Arial", 16)).pack(side='right')
        see = tk.Label(row_icon_btns, text=icons.SEE_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
        see.bind('<Button-1>', lambda e: FileOpen.see_file(mof.filepath))
        see.pack(side='right')
        tk.Label(row_icon_btns, text="  ", font=("Arial", 16)).pack(side='right')
        edit = tk.Label(row_icon_btns, text=icons.EDIT_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
        edit.bind('<Button-1>', lambda e: select_for_edit(parent, mof))
        edit.pack(side='right')
        row_icon_btns.grid(sticky=tk.E, row=0, column=2)

        self.attribute_row = self.generate_attribute_row()

        self.generate_sbu_row().grid(sticky=tk.EW, columnspan=3)

        row4 = tk.Frame(master=self, height=20)
        ligand_label = tk.Label(row4, text="Ligands:")
        ligand_label.pack(side='left')
        row4.grid(sticky=tk.EW, columnspan=3)

    def generate_sbu_row(self):
        attribute_row = tk.Frame(master=self, height=20)
        sbu_label = tk.Label(attribute_row, text="SBUs:")
        sbu_label.pack(side='left')
        for node in self.sbus.clusters:
            self.display_sbu_name(attribute_row, node, '#0000a0')
        for conn in self.sbus.connectors:
            self.display_sbu_name(attribute_row, conn, '#008100')
        for aux in self.sbus.auxiliaries:
            self.display_sbu_name(attribute_row, aux, '#810000')
        return attribute_row

    def display_sbu_name(self, parent, sbu, color):
        text = f"{sbu.frequency}x {sbu.label} ({sbu.connections()}*)"
        sbu_label = tk.Label(parent, text=text, fg=color, cursor=icons.LINK_CURSOR, padx=3)
        f = tkFont.Font(sbu_label, sbu_label["font"])
        f.configure(underline=True)
        sbu_label.configure(font=f)
        event_function = self.have_page_highlight(sbu)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')

    def have_page_highlight(self, clicked_node):
        def fun(*args):
            self.top_page.highlight_molecule(clicked_node)
        return fun

    def refresh_attributes(self):
        self.attribute_row.grid_forget()
        self.attribute_row = self.generate_attribute_row()

    def generate_attribute_row(self):
        row = tk.Frame(master=self, height=20)
        i = 0
        for text, attr in Attributes.attributes.items():
            if attr.enabled:
                _attribute_view(row, text, attr.calculate(self.mof), attr.description).grid(column=i, row=0, sticky=tk.EW)
                row.grid_columnconfigure(i, weight=1)
                i += 1
        row.grid(sticky=tk.EW, row=1, columnspan=3)
        return row


def _attribute_view(parent, name, value, description):
    view = tk.Frame(parent, bd=0, relief=tk.SOLID)
    view.config(highlightbackground='#ffffff', highlightcolor="#ffffff", highlightthickness=1)
    top = tk.Label(view, text=name)
    Tooltips.create_tool_tip(top, description)
    top.pack()
    bottom = tk.Label(view, text=value)
    bottom.pack()
    return view