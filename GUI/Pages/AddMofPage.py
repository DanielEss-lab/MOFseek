import tkinter as tk
from GUI.Pages.AddMOF import OpenMofsView, StoreMofsView


class Page(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.mofs = []
        self.OpenMofsView = OpenMofsView.Page(self)
        self.OpenMofsView.pack()
        self.StoreMofsView = StoreMofsView.Page(self)
        self.StoreMofsView.pack()

    def refresh_attributes_shown(self):
        self.OpenMofsView.refresh_attributes_shown()

    def set_source_name_suggestions(self):
        self.StoreMofsView.set_source_name_suggestions()

    def enable_store_button(self):
        self.StoreMofsView.enable_store_button()

    def empty_selected_mofs_display(self):
        self.OpenMofsView.empty_display()
