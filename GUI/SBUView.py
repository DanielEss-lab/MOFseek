import tkinter as tk

from MofIdentifier.fileIO import FileOpen


def make_view(parent, sbu):
    view = tk.Frame(parent, height=40, width=80, bd=1, relief=tk.SOLID)

    row1 = tk.Frame(master=view, height=20)
    name = tk.Label(row1, text=sbu.label)
    name.pack(side='left')
    search = tk.Label(row1, text="Search as Ligand", cursor='hand2', padx=8)
    search.bind('<Button-1>', lambda e: parent.search_v.force_search_for(sbu))
    search.pack(side='right')
    open = tk.Label(row1, text="Open File", cursor='hand2', padx=8)
    open.bind('<Button-1>', lambda e: FileOpen.open_file(sbu.filepath))
    open.pack(side='right')
    see = tk.Label(row1, text="Reveal File", cursor='hand2', padx=8)
    see.bind('<Button-1>', lambda e: FileOpen.see_file(sbu.filepath))
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
    sbu_search = tk.Label(row3, text="See Details", cursor='hand2', padx=8)
    sbu_search.bind('<Button-1>', lambda e: parent.search_v.force_search_sbu(sbu))
    sbu_search.pack(side='right')
    row3.pack(fill=tk.X)

    return view
