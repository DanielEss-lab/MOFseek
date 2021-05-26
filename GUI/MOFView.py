import tkinter as tk


def make_view(parent, mof):
    view = tk.Frame(parent, height=40, width=40, bd=2, relief=tk.SOLID)

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
