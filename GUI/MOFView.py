import tkinter as tk
import tkinter.font as tkFont

from GUI import Tooltips
from GUI.Search import Attributes
from MofIdentifier.fileIO import FileOpen
from MofIdentifier.subbuilding import SBUCollectionManager, SBUIdentifier


def format_elements(mof):
    elements = list(mof.elementsPresent)
    elements.sort()
    return ' '.join(elements)


def make_view(parent, mof):
    sbus = SBUCollectionManager.process_new_mof(mof)
    root = parent.master.master
    view = tk.Frame(parent, height=40, bd=1, relief=tk.SOLID)
    row1 = tk.Frame(master=view)
    name = tk.Label(row1, text=mof.label, font=("Arial", 10))
    name.pack(side='left')
    open = tk.Label(row1, text="\U0001F441", cursor='hand2', padx=2, font=("Arial", 16), height=0)
    open.bind('<Button-1>', lambda e: FileOpen.open_file(mof.filepath))
    open.pack(side='right')
    tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
    see = tk.Label(row1, text="\U0001f4c1", cursor='hand2', padx=2, font=("Arial", 16), height=0)
    see.bind('<Button-1>', lambda e: FileOpen.see_file(mof.filepath))
    see.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view, height=20)
    attributes = Attributes.get_attributes(mof)
    for text, value in attributes.items():
        _attribute_view(row2, text, value, Attributes.attribute_descriptions[text]).pack(side='left')
    _attribute_view(row2, 'Elements', format_elements(mof),
                    'Atomic symbols of elements present in MOF').pack(side='left')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=20)
    sbu_label = tk.Label(row3, text="SBUs:")
    sbu_label.pack(side='left')

    def have_root_highlight(clicked_node):
        def fun(*args):
            root.highlight_molecule(clicked_node)
        return fun

    def display_sbu_name(sbu, color):
        text = f"{sbu.frequency}x {sbu.label} ({sbu.connections()}\u00B0)"
        sbu_label = tk.Label(row3, text=text, fg=color, cursor='hand2', padx=3)
        f = tkFont.Font(sbu_label, sbu_label["font"])
        f.configure(underline=True)
        sbu_label.configure(font=f)
        event_function = have_root_highlight(sbu)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')

    for node in sbus.clusters:
        display_sbu_name(node, '#0000a0')
    for conn in sbus.connectors:
        display_sbu_name(conn, '#008100')
    for aux in sbus.auxiliaries:
        display_sbu_name(aux, '#810000')
    row3.pack(fill=tk.X)

    row4 = tk.Frame(master=view, height=20)
    ligand_label = tk.Label(row4, text="Ligands:")
    ligand_label.pack(side='left')
    row4.pack(fill=tk.X)

    return view


def _attribute_view(parent, name, value, description):
    view = tk.Frame(parent, bd=1, relief=tk.SOLID)
    top = tk.Label(view, text=name)
    Tooltips.create_tool_tip(top, description)
    top.pack()
    bottom = tk.Label(view, text=value)
    bottom.pack()
    return view
