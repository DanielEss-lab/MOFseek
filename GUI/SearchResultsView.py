import os
import time
import tkinter as tk
import tkinter.filedialog as fd

from GUI import MOFView
from GUI.Search import Attributes


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=450, width=800)
        self.results = []

        self.selected_sort = tk.StringVar(self)
        self.default_sort_string = 'Sort by: \u25BC'
        sort_options = [self.default_sort_string]
        for attr in Attributes.attribute_names:
            sort_options.append(attr + ' | high first')
            sort_options.append(attr + ' | low first')
        self.selected_sort.set(sort_options[0])
        sort_dropdown = tk.OptionMenu(self, self.selected_sort, *sort_options,
                                      command=lambda _: self.display_results(self.results))
        sort_dropdown.config(indicatoron=0)
        sort_dropdown.pack()

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
        self.btn_export = tk.Button(self, text='Export Results', command=lambda: self.export())
        self.btn_export['state'] = "disabled"
        self.btn_export.pack()

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
        sort_name = self.selected_sort.get()
        if sort_name == self.default_sort_string:
            pass
        else:
            division_index = sort_name.rfind('|')
            attribute = sort_name[:division_index-1]
            descending = sort_name[division_index+1:].find('high first') >= 0
            results.sort(reverse=descending, key=lambda mof: Attributes.get_attributes(mof)[attribute])
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
        if len(results) > 0:
            self.btn_export['state'] = "normal"
        else:
            self.btn_export['state'] = "disabled"

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
