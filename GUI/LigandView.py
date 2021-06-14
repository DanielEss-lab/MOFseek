import tkinter as tk

from MofIdentifier.fileIO import FileOpen
import tkinter.font as tkFont


def make_view(parent, ligand):
    view = tk.Frame(parent, height=40, width=120, bd=1, relief=tk.SOLID)

    row1 = tk.Frame(master=view)
    name = tk.Label(row1, text=ligand.label)
    name.pack(side='left')
    open = tk.Label(row1, text="\U0001F441", cursor='hand2', padx=2, font=("Arial", 14), height=0)
    open.bind('<Button-1>', lambda e: FileOpen.open_file(ligand.filepath))
    open.pack(side='right')
    tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
    see = tk.Label(row1, text="\U0001f4c1", cursor='hand2', padx=2, font=("Arial", 14), height=0)
    see.bind('<Button-1>', lambda e: FileOpen.see_file(ligand.filepath))
    see.pack(side='right')
    search = tk.Label(row1, text="Search as SBU", cursor='hand2', padx=8)
    f = tkFont.Font(search, search["font"])
    f.configure(underline=True)
    search.configure(font=f)
    search.bind('<Button-1>', lambda e: parent.search_v.force_search_sbu(ligand))
    search.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view)
    elements = tk.Label(row2, text=ligand.atoms_string())
    elements.pack(side='left')
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=10)
    sbu_label = tk.Label(row3, text="<NYI> Occurrences in DB")
    sbu_label.pack(side='left')
    row3.pack(fill=tk.X)

    row4 = tk.Frame(master=view, height=20)
    mof_label = tk.Label(row4, text="MOFs:")
    mof_label.pack(side='left')
    sbu_search = tk.Label(row4, text="Search", cursor='hand2', padx=8)
    f = tkFont.Font(sbu_search, sbu_search["font"])
    f.configure(underline=True)
    sbu_search.configure(font=f)
    sbu_search.bind('<Button-1>', lambda e: parent.search_v.force_search_for(ligand))
    sbu_search.pack(side='right')
    row4.pack(fill=tk.X)

    return view