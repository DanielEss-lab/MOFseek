import os
import time
import tkinter as tk
import tkinter.filedialog as fd

from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import MultiMofView
from GUI import Attributes, Settings
from MofIdentifier.fileIO import MoleculeWriter, CifWriter


class View(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda results: self.display_results(results))
        self.results = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.selected_sort = tk.StringVar(self)
        self.default_sort_string = 'Sort by: \u25BC'
        self.sort_options = self.build_sort_options()
        self.selected_sort.set(self.sort_options[0])
        self.sort_dropdown = self.build_sort_dropdown()

        self.lbl_num_results = tk.Label(self, width=30, anchor=tk.W)
        self.lbl_num_results.grid(row=2, column=0, padx=2, sticky=tk.W)

        self.main_body = MultiMofView.View(self)
        self.main_body.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW)

        self.export_frm = tk.Frame(self)
        self.btn_export_txt = StyledButton.make(self.export_frm, text='Export names as .txt', command=self.export_txt)
        self.btn_export_txt['state'] = "disabled"
        self.btn_export_txt.pack(side=tk.LEFT)
        self.btn_export_cifs = StyledButton.make(self.export_frm, text='Export MOF CIFs', command=self.export_cifs)
        self.btn_export_cifs['state'] = "disabled"
        self.btn_export_cifs.pack(side=tk.LEFT)
        self.export_frm.grid(row=2, column=2, padx=2, sticky=tk.E)

    def add_error_to_layout(self, error_row):
        error_row.grid(row=1, column=1, padx=2)

    def add_progress_to_layout(self, progress):
        progress.grid(row=0, column=1, padx=2, sticky=tk.EW)

    def add_cancel_to_layout(self, btn_cancel):
        btn_cancel.grid(row=0, column=0, padx=2)

    def display_results(self, results):
        sort_name = self.selected_sort.get()
        if sort_name == self.default_sort_string:
            pass
        else:
            division_index = sort_name.rfind('|')
            attribute = sort_name[:division_index-1]
            descending = sort_name[division_index+1:].find('high first') >= 0
            results.sort(reverse=descending, key=lambda mof: Attributes.attributes[attribute].calculate(mof))
        self.results = results
        if len(self.results) > 0:
            self.lbl_num_results['text'] = f"{len(results)} Results"
            self.btn_export_txt['state'] = "normal"
            self.btn_export_cifs['state'] = "normal"
        else:
            self.lbl_num_results['text'] = "No Results"
            self.btn_export_txt['state'] = "disabled"
            self.btn_export_cifs['state'] = "disabled"
        self.main_body.display_results(results)

    def export_cifs(self):
        if len(self.results) == 0:
            return
        path = fd.askdirectory()
        if not Settings.keep_solvent:
            for molecule in self.results:
                CifWriter.write_without_solvent(molecule, path)
        else:
            MoleculeWriter.write_many((mof.get_mof() for mof in self.results), path)

    def export_txt(self):
        if len(self.results) == 0:
            return
        f = fd.asksaveasfile(mode='w', defaultextension=".txt", title="Export results",
                             initialdir=os.getcwd(), initialfile='SearchOutput' + str(time.time()))
        if f is None:
            return
        text_to_save = '\n'.join(mof.filename for mof in self.results)
        f.write(text_to_save)
        f.close()

    def rebuild_sort_dropdown(self):
        self.sort_options = self.build_sort_options()
        self.sort_dropdown.grid_forget()
        self.sort_dropdown = self.build_sort_dropdown()

    def build_sort_dropdown(self):
        sort_dropdown = tk.OptionMenu(self, self.selected_sort, *self.sort_options,
                                           command=lambda _: self.start_process(self.results))
        sort_dropdown.config(indicatoron=0)
        sort_dropdown.grid(row=2, column=1, padx=2)
        return sort_dropdown

    def build_sort_options(self):
        sort_options = [self.default_sort_string]
        for name, attr in Attributes.attributes.items():
            if attr.enabled and (attr.var_type is int or attr.var_type is float):
                sort_options.append(name + ' | high first')
                sort_options.append(name + ' | low first')
        return sort_options
