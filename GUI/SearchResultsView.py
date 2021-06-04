import os
import time
import tkinter as tk
import tkinter.filedialog as fd

from GUI import MOFView


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=450, width=800, bd=2, relief=tk.SOLID)
        self.results = []
        mainBody = tk.Frame(self, height=400, width=800, bd=1, relief=tk.SOLID)
        self.canvas = tk.Canvas(mainBody, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.canvas.master = parent
        self.vsb = tk.Scrollbar(mainBody, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.on_frame_configure)
        # self.frame.bind('<Configure>', self._configure_window)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        mainBody.pack(fill=tk.X)
        btn_export = tk.Button(self, text='Export Results', command=lambda: self.export())
        btn_export.pack()

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
        lbl_num_results = tk.Label(self.frame, text=f"{len(results)} Results")
        lbl_num_results.grid(sticky=("N", "S", "W"))
        for mof in results:
            mof_v = MOFView.make_view(self.frame, mof)
            mof_v.grid(sticky=("N", "S", "E", "W"))

    def export(self):
        if len(self.results) == 0:
            return
        f = fd.asksaveasfile(mode='w', defaultextension=".txt", title="Export results",
                             initialdir=os.getcwd(), initialfile='SearchOutput' + str(time.time()))
        if f is None:
            return
        text_to_save = '\n'.join(mof.label for mof in self.results)
        f.write(text_to_save)
        f.close()
