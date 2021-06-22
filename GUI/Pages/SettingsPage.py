import tkinter as tk
import tkinter.ttk as ttk

from GUI.Search import Attributes

instruction_text = """Select which properties you would like to search by and see for each MOF. """


class Page(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.grid()

        for attr in Attributes.attributes:
            Page.AttributeSetting(self, attr).grid(sticky=tk.W)

    class AttributeSetting(tk.Frame):
        def __init__(self, parent, attribute_name):
            self.parent = parent
            self.name = attribute_name
            super().__init__(self.parent)
            self.is_enabled = tk.IntVar(value=1 if Attributes.attributes[self.name].enabled else 0)

            def change_settings():
                Attributes.attributes[self.name].enabled = self.is_enabled.get()
                self.winfo_toplevel().toggle_attribute()

            btn = ttk.Checkbutton(self, variable=self.is_enabled, command=change_settings, style='TCheckbutton')
            lbl = tk.Label(self, text=self.name + ': ' + Attributes.attributes[self.name].description)
            btn.pack(side=tk.LEFT)
            lbl.pack(side=tk.LEFT)

    class Setting(tk.Frame):
        def __init__(self, parent, attribute_name):
            self.parent = parent
            self.name = attribute_name
            super().__init__(self.parent)
            self.is_enabled = tk.IntVar(value=1 if Attributes.attributes[self.name].enabled else 0)

            def change_settings():
                Attributes.attributes[self.name].enabled = self.is_enabled.get()
                self.winfo_toplevel().toggle_attribute()

            btn = ttk.Checkbutton(self, text=self.name, variable=self.is_enabled, onvalue=1, offvalue=0,
                                 command=change_settings)
            lbl = tk.Label(self, text=Attributes.attributes[self.name].description)
            btn.pack(side=tk.LEFT)
            lbl.pack(side=tk.LEFT)
