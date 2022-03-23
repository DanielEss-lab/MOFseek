import tkinter as tk
from GUI import Settings
from GUI.Utility import FrameWithProcess, StyledButton, AutoCompleteComboBox
from DAOsAndServices import MOFDAO

instruction_text = """The selected MOFs will be loaded onto the database, and the rest of their properties will be 
calculated. The calculations will take some time (expect 2-5 minutes per MOF for this step), so please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda mofs: self.add_mofs_to_db(mofs))
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        row1 = tk.Frame(self)
        source_name_instructions = tk.Label(row1, text="Source Database: ", justify=tk.LEFT)
        source_name_instructions.pack(side=tk.LEFT)
        self.source_name_ent = AutoCompleteComboBox.Box(row1)
        self.set_source_name_suggestions()
        self.source_name_ent.pack(side=tk.LEFT)
        row1.pack()
        self.add_btn = StyledButton.make(self, text='Upload to DB', command=lambda: self.start_process(self.parent.mofs))
        self.add_btn['state'] = "disabled"
        self.add_btn.pack()

    def add_mofs_to_db(self, mofs):
        source_name = self.source_name_ent.get()
        if source_name == "":
            self._show_error("Must input a name for the source database")
            return
        else:
            self.source_name_ent.delete(0, tk.END)
        Settings.add_source_name(source_name)
        self.parent.winfo_toplevel().update_sources_settings()
        self.add_btn['state'] = "disabled"
        self.parent.empty_selected_mofs_display()
        for mof in mofs:
            MOFDAO.add_mof(mof, source_name)
        self.parent.winfo_toplevel().forget_history()
        self.parent.mofs = []

    def set_source_name_suggestions(self):
        self.source_name_ent.set_completion_list(Settings.current_source_states().keys())

    def enable_store_button(self):
        self.add_btn['state'] = "active"
