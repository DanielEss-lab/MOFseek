import tkinter as tk

from GUI import MainWindow
from MofIdentifier.subbuilding import SBUIdentifier, SBUCollectionManager


def make_view(parent, mof):
    root = parent.master.master
    view = tk.Frame(parent, height=40, bd=2, relief=tk.SOLID)
    row1 = tk.Frame(master=view, height=20)
    name = tk.Label(row1, text=mof.label)
    name.pack(side='left')
    open = tk.Label(row1, text="<NYI: open>")
    open.pack(side='right')
    see = tk.Label(row1, text="<NYI: see>")
    see.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view, height=20)
    attributes = [
        "Pore Size (mm):",
        "Surface Area (mm):",
        "Volume (mL/mol)",
        "Conductivity (Ohms)",
        "Fav Food",
        "Weight (mG)",
        "Postal Code",
        "Fictitious val",
    ]
    for idx, text in enumerate(attributes[::-1]):
        _attribute_view(row2, text, idx).pack(side='right')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=20)
    sbu_label = tk.Label(row3, text="SBUs:")
    sbu_label.pack(side='left')
    (new_sbus, recognized_sbus) = SBUCollectionManager.process_new_mof(mof)
    sbus = new_sbus + recognized_sbus
    for node in sbus.clusters:
        text = f"{node.frequency}x{node.label} ({node.connections()} connections)"
        sbu_label = tk.Label(row3, text=text, fg='#0000a0', cursor='hand2', padx=2)
        sbu_label.pack(side='left')
        sbu_label.bind('<Button-1>', lambda e: root.highlight_molecule(node))
    for conn in sbus.connectors:
        text = f"{conn.frequency}x{conn.label} ({conn.connections()} connections)"
        sbu_label = tk.Label(row3, text=text, fg='#008100', cursor='hand2', padx=2)
        sbu_label.pack(side='left')
        sbu_label.bind('<Button-1>', lambda e: root.highlight_molecule(conn))
    for aux in sbus.auxiliaries:
        text = f"{aux.frequency}x{aux.label} ({aux.connections()} connections)"
        sbu_label = tk.Label(row3, text=text, fg='#810000', cursor='hand2', padx=2)
        sbu_label.pack(side='left')
        sbu_label.bind('<Button-1>', lambda e: root.highlight_molecule(aux))
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
