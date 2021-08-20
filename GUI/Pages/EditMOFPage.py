import tkinter as tk

from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import MOFView

instruction_text = """Choose a MOF from the Search page, and then edit it from this page. Saving the edits to the 
database may take some time. Please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda new_mof: self.edit_mof_in_db(new_mof))
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.mof_frame = tk.Frame(self)
        self.mof_frame.pack()
        self.mofView = None
        self.edit_button = StyledButton.make(self, text="Save Edits",
                                             command=lambda: self.start_process(self.assemble_new_mof()))
        self.edit_button.pack()
        self.mof = None

    def select_mof(self, mof):
        if self.mofView is not None:
            self.mofView.pack_forget()
        self.mof = mof
        self.mofView = MOFView.View(self.mof_frame, mof)
        self.mofView.pack()

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

    def refresh_attributes_shown(self):
        if self.mof is not None:
            self.select_mof(self.mof)
