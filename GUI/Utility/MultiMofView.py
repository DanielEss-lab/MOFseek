from _tkinter import TclError
import tkinter as tk

from GUI.Views import MOFView


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=450, width=800)
        self.results = []

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", height=400)
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.canvas.master = parent
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.on_frame_configure)
        # self.frame.bind('<Configure>', self._configure_window)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

    def on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def display_results(self, results):
        self.results = results
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.focus_set()
        self.canvas.yview_moveto(0)
        for mof in results:
            mof_v = MOFView.View(self.frame, mof)
            mof_v.grid(sticky=("N", "S", "E", "W"))

    def refresh_all_attributes(self):
        for widget in self.frame.winfo_children():
            widget.refresh_attributes()
