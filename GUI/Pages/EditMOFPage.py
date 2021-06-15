import tkinter as tk

from GUI.Utility import FrameWithProcess
from GUI.Views import MOFView

instruction_text = """Choose a MOF from the Search page, and then edit it from this page. Saving the edits to the 
database may take some time. Please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.custom_ligands = dict()
        super().__init__(self.parent, lambda new_mof: self.edit_mof_in_db(new_mof))
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.mof_frame = tk.Frame(self)
        self.mof_frame.pack()
        self.molecule_v = None
        self.edit_button = tk.Button(self, text="Save Edits",
                                       command=lambda: self.start_process(self.assemble_new_mof()))
        self.edit_button.pack()
        self.mof = None

    def select_mof(self, mof):
        self.mof = mof
        mofView = MOFView.make_view(self.mof_frame, mof)
        mofView.pack()

    def edit_mof_in_db(self, new_mof):
        if self.mof is not None:
            if new_mof is not None:
                # TODO: link to DAO
                pass
            else:
                self._show_error('Unable to process edits into valid MOF in order to save to db')
        else:
            self._show_error('No MOF selected to edit')

    def assemble_new_mof(self):
        return None  # DatabaseMOFPojo(self.entry.get())