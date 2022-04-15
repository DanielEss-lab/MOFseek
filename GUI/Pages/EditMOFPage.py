import tkinter as tk

from DAOsAndServices import DeleteService, MOFDAO
from GUI import Settings
from GUI.Utility import FrameWithProcess, StyledButton, AutoCompleteComboBox
from GUI.Views import MOFView

instruction_text = """Choose a MOF, either here or from the Search page, and then delete it from this page. 
There is no undo button."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda _: self.delete_mof_from_db())
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.combobox = AutoCompleteComboBox.Box(self, ("Arial", 10), self.select_mof)
        self.combobox.pack()
        self.values = self.all_mof_names()
        self.combobox.set_completion_list(self.values)
        self.combobox.focus_set()
        self.mof_frame = tk.Frame(self)
        self.mof_frame.pack()
        self.mofView = None
        self.edit_button = StyledButton.make(self, text="Delete",
                                             command=lambda: self.start_process(None))  # Delete button for now
        self.edit_button['state'] = "disabled"
        self.edit_button.pack()
        self.mof = None

    def select_mof(self, mof_name):
        if self.mofView is not None:
            self.mofView.pack_forget()
        self.mof = MOFDAO.get_MOF(mof_name)
        self.mofView = MOFView.View(self.mof_frame, self.mof)
        self.mofView.pack()
        self.edit_button['state'] = "active"

    def delete_mof_from_db(self):
        if self.mof is not None:
            DeleteService.delete_mof(self.mof.filename)
            self.edit_button['state'] = "disabled"
            self.mofView.pack_forget()
            self.mofView = None
            self.check_to_delete_source()
            self.mof = None
            self.parent.winfo_toplevel().mofs_added_or_removed()
        else:
            self._show_error('No MOF selected to delete')

    def refresh_attributes_shown(self):
        if self.mof is not None:
            self.select_mof(self.mof)

    def all_mof_names(self):
        return MOFDAO.get_all_names()

    def reset_mof_names(self):
        self.values = self.all_mof_names()
        self.combobox.set_completion_list(self.values)

    def check_to_delete_source(self):
        for source_name in self.mof.source_names:
            if not MOFDAO.any_mofs_have_source(source_name):
                Settings.delete_source_name(source_name)
                self.parent.winfo_toplevel().update_sources_settings()
