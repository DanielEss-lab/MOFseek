import os
import time
import tkinter as tk
import tkinter.filedialog as fd

from GUI.Utility import MultiMofView
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

        self.main_body = MultiMofView.View(self)

        self.main_body.pack(fill=tk.X)
        self.btn_export = tk.Button(self, text='Export Results', command=lambda: self.export())
        self.btn_export['state'] = "disabled"
        self.btn_export.pack()

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
        self.btn_export['state'] = "normal"
        self.main_body.display_results(results)

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
