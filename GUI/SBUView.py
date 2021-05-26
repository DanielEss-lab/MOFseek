import tkinter as tk


def make_view(parent, sbu):
    view = tk.Frame(parent, height=40, width=40, bd=1, relief=tk.SOLID)

    row1 = tk.Frame(master=view, height=20)
    name = tk.Label(row1, text=sbu.label)
    name.pack(side='left')
    open = tk.Label(row1, text="<NYI: open>")
    open.pack(side='right')
    see = tk.Label(row1, text="<NYI: see>")
    see.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view, height=10)
    sbu_label = tk.Label(row2, text=str(sbu.frequency) + " Occurrences in DB")
    sbu_label.pack(side='left')
    type = tk.Label(row2, text=str(sbu.type))
    type.pack(side='right')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=20)
    mof_label = tk.Label(row3, text="MOFs:")
    mof_label.pack(side='left')
    row3.pack(fill=tk.X)

    return view
