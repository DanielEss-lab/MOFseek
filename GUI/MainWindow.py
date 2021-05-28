import tkinter as tk

from GUI import MOFView, SBUView, SearchView, SearchResultsView, MoleculeView, UploadLigandView
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier

instance = None


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Ess lab | P66 | GUI WIP")
        # frame = tk.Frame(self, bg="white", bd='5')  # background
        # frame.pack(side='bottom')
        # button = tk.Button(frame, text='Close Window', width=10, height=3, command=self.destroy)
        # button.pack()
        # button2 = ttk.Button(frame, text='Close Window?!', command=self.destroy)
        # button2.pack()
        # greeting = tk.Label(frame, text="Hello, Tkinter", fg="blue", anchor=tk.S)  # foreground
        # greeting.pack()  # Change the label by binding it to a Tkinter variable using textvariable= ?
        # entry = tk.Entry(frame, fg="#222222", bg="#cccccc", width=50)
        # entry.pack()  # To get text: entry.get()
        # text_box = tk.Text()
        # text_box.pack()  # To get text: text_box.get("1.0",tk.END)  # 1 means first line, 0 means first character.
        # frame1 = tk.Frame(self, bg="#ccccff", relief=tk.GROOVE, borderwidth=10)  # background
        # frame1.pack(side=tk.LEFT)
        # label1 = tk.Label(master=frame1, text='Second Frame')
        # label1.pack()

        # mof = CifReader.get_mof('../MofIdentifier/mofsForTests/smod7-pos-1.cif')
        # sbus = SBUIdentifier.split(mof)
        # mof_v = MOFView.make_view(self, mof)
        # mof_v.pack(fill=tk.X)
        # for sbu in sbus.clusters + sbus.connectors + sbus.auxiliaries:
        #     SBUView.make_view(self, sbu).pack()
        # self.minsize(100, 100)
        self.geometry('800x500')

        self.upload_mof_v = UploadLigandView.View(self)
        self.upload_mof_v.pack()
        self.search_v = SearchView.make_view(self)
        self.search_v.pack()
        self.search_results_v = SearchResultsView.View(self)
        self.search_results_v.pack(fill=tk.X)

        self.molecule_v = None

    def display_search_results(self, results):
        self.search_results_v.display_results(results)

    def highlight_molecule(self, mol):
        if self.molecule_v is not None:
            self.molecule_v.destroy()
        self.molecule_v = MoleculeView.make_view(self, mol)
        self.molecule_v.pack(side=tk.BOTTOM)
