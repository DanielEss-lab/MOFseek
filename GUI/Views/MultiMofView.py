import tkinter as tk

from GUI.Utility.ScrollFrame import ScrollFrame
from GUI.Views import MOFView


class View(ScrollFrame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, height=450)
        self.results = []

        self.mofs_frame = super().get_frame()
        self.mofs_frame.grid_columnconfigure(0, weight=1)

    def display_results(self, results):
        self.results = results
        for widget in self.mofs_frame.winfo_children():
            widget.destroy()
        self.mofs_frame.focus_set()
        self.canvas.yview_moveto(0)
        num_shown = 0
        for mof in results:
            mof_v = MOFView.View(self.mofs_frame, mof)
            mof_v.grid(sticky=tk.EW)
            num_shown += 1
            if num_shown >= 100:
                break

    def refresh_all_attributes(self):
        for widget in self.mofs_frame.winfo_children():
            widget.refresh_attributes()

    def refresh_all_elements(self):
        for widget in self.mofs_frame.winfo_children():
            widget.refresh_elements()
