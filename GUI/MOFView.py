import tkinter as tk

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
    view = tk.Frame(parent, height=40, bd=2, relief=tk.SOLID)
    row1 = tk.Frame(master=view, height=20)
    name = tk.Label(row1, text=mof.label)
    name.pack(side='left')
    open = tk.Label(row1, text="Open File", cursor='hand2', padx=8)
    open.bind('<Button-1>', lambda e: FileOpen.open_file(mof.filepath))
    open.pack(side='right')
    see = tk.Label(row1, text="Reveal File", cursor='hand2', padx=8)
    see.bind('<Button-1>', lambda e: FileOpen.see_file(mof.filepath))
    see.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view, height=20)
    attributes = Attributes.get_attributes(mof)
    for text, value in attributes.items():
        _attribute_view(row2, text, value).pack(side='left')
    _attribute_view(row2, 'Elements', format_elements(mof)).pack(side='left')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=20)
    sbu_label = tk.Label(row3, text="SBUs:")
    sbu_label.pack(side='left')

    def have_root_highlight(clicked_node):
        def fun(*args):
            root.highlight_molecule(clicked_node)
        return fun

    for node in sbus.clusters:
        text = f"{node.frequency}x {node.label} (c {node.connections()})"
        sbu_label = tk.Label(row3, text=text, fg='#0000a0', cursor='hand2', padx=3)
        event_function = have_root_highlight(node)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')
    for conn in sbus.connectors:
        text = f"{conn.frequency}x {conn.label} (c {conn.connections()})"
        sbu_label = tk.Label(row3, text=text, fg='#008100', cursor='hand2', padx=3)
        event_function = have_root_highlight(conn)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')
    for aux in sbus.auxiliaries:
        text = f"{aux.frequency}x {aux.label} (c {aux.connections()})"
        sbu_label = tk.Label(row3, text=text, fg='#810000', cursor='hand2', padx=3)
        event_function = have_root_highlight(aux)
        sbu_label.bind('<Button-1>', event_function)
        sbu_label.pack(side='left')
    row3.pack(fill=tk.X)

    row4 = tk.Frame(master=view, height=20)
    ligand_label = tk.Label(row4, text="Ligands:")
    ligand_label.pack(side='left')
    row4.pack(fill=tk.X)

    return view


def _attribute_view(parent, name, value):
    view = tk.Frame(parent, bd=1, relief=tk.SOLID)
    top = tk.Label(view, text=name)
    top.pack()
    bottom = tk.Label(view, text=value)
    bottom.pack()
    return view
