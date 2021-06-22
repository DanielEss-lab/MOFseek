import tkinter as tk

from GUI import icons
from MofIdentifier.fileIO import FileOpen
import tkinter.font as tkFont


def select_for_edit(parent, sbu):
    parent.winfo_toplevel().select_sbu_for_edit(sbu)


def make_view(parent, sbu):
    view = tk.Frame(parent, height=40, width=120, bd=1, relief=tk.SOLID)

    row1 = tk.Frame(master=view)
    name = tk.Label(row1, text=sbu.label)
    name.pack(side='left')
    open = tk.Label(row1, text=icons.OPEN_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
    open.bind('<Button-1>', lambda e: FileOpen.open_file(sbu.filepath))
    open.pack(side='right')
    tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
    see = tk.Label(row1, text=icons.SEE_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 14), height=0)
    see.bind('<Button-1>', lambda e: FileOpen.see_file(sbu.filepath))
    see.pack(side='right')
    tk.Label(row1, text="  ", font=("Arial", 16)).pack(side='right')
    edit = tk.Label(row1, text=icons.EDIT_ICON, cursor=icons.LINK_CURSOR, padx=2, font=("Arial", 16), height=0)
    edit.bind('<Button-1>', lambda e: select_for_edit(parent, sbu))
    edit.pack(side='right')
    search = tk.Label(row1, text="Search as Ligand", cursor=icons.LINK_CURSOR, padx=8)
    f = tkFont.Font(search, search["font"])
    f.configure(underline=True)
    search.configure(font=f)
    search.bind('<Button-1>', lambda e: parent.winfo_toplevel().force_search_ligand(sbu))
    search.pack(side='right')
    row1.pack(fill=tk.X)

    row2 = tk.Frame(master=view)
    file_first_line = sbu.file_content.partition('\n')[0]
    first_line_label = tk.Label(row2, text=file_first_line)
    first_line_label.pack(side=tk.RIGHT)
    elements = tk.Label(row2, text=sbu.atoms_string())
    elements.pack(side=tk.LEFT)
    row2.pack(fill=tk.X)

    row3 = tk.Frame(master=view, height=10)
    # FIXME: change when it I connect to DB, so that I always get SBU objects and I actually show frequency
    sbu_label = tk.Label(row3, text="<NYI> Occurrences in DB")
    sbu_label.pack(side='left')
    # type = tk.Label(row3, text=str(sbu.type))  # TODO_Also uncomment this
    # type.pack(side='right')
    row3.pack(fill=tk.X)

    row4 = tk.Frame(master=view, height=20)
    mof_label = tk.Label(row4, text="MOFs:")
    mof_label.pack(side='left')
    sbu_search = tk.Label(row4, text="Search", cursor=icons.LINK_CURSOR, padx=8)
    f = tkFont.Font(sbu_search, sbu_search["font"])
    f.configure(underline=True)
    sbu_search.configure(font=f)
    sbu_search.bind('<Button-1>', lambda e: parent.winfo_toplevel().force_search_sbu(sbu))
    sbu_search.pack(side='right')
    row4.pack(fill=tk.X)

    return view
