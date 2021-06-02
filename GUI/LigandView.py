import tkinter as tk


def make_view(parent, ligand):
    view = tk.Frame(parent, height=40, width=80, bd=1, relief=tk.SOLID)

    row1 = tk.Frame(master=view, height=20)
    name = tk.Label(row1, text=ligand.label)
    name.pack(side='left')
    open = tk.Label(row1, text="<NYI: open>")
    open.pack(side='right')
    see = tk.Label(row1, text="<NYI: see>")
    see.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view, height=10)
    sbu_label = tk.Label(row2, text=str(ligand.frequency) + " Occurrences in DB")
    sbu_label.pack(side='left')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=20)
    mof_label = tk.Label(row3, text="MOFs:")
    mof_label.pack(side='left')
    row3.pack(fill=tk.X)

    return view