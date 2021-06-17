import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilenames

from GUI.Search import Attributes
from GUI.Utility import FrameWithProcess, MultiMofView, Tooltips
from MofIdentifier.fileIO import CifReader

instruction_text = """Select which properties you would like to see for each MOF and have the option to sort by. Recommended amount: less than 10"""


class Page(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.grid()

        for attr in Attributes.attributes:
            Page.AttributeRow(self, attr).grid(sticky=tk.W)

    class AttributeRow(tk.Frame):
        def __init__(self, parent, attribute_name):
            self.parent = parent
            self.name = attribute_name
            super().__init__(self.parent)
            self.is_enabled = tk.IntVar(value=1 if Attributes.attributes[self.name].enabled else 0)

            def change_settings():
                Attributes.attributes[self.name].enabled = self.is_enabled.get()
                if self.is_enabled.get():
                    self.winfo_toplevel().enable_attribute(self.name)
                else:
                    self.winfo_toplevel().disable_attribute(self.name)

            btn = tk.Checkbutton(self, text=self.name, variable=self.is_enabled, onvalue=1, offvalue=0,
                                 command=change_settings)
            lbl = tk.Label(self, text=Attributes.attributes[self.name].description)
            btn.pack(side=tk.LEFT)
            lbl.pack(side=tk.LEFT)
