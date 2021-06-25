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

        Page.Setting(self, 'SBU search', 'Enable the powerful (but situational) SBU search', 0,
                     lambda enabled: self.winfo_toplevel().toggle_sbu_search(enabled)).grid(sticky=tk.W, pady=(20,0))

    class Setting(tk.Frame):
        def __init__(self, parent, name, description, starts_enabled, function):
            self.parent = parent
            self.name = name
            super().__init__(self.parent)
            self.is_enabled = tk.IntVar(value=starts_enabled)

            def change_setting():
                enabled = self.is_enabled.get()
                function(enabled)

            btn = ttk.Checkbutton(self, variable=self.is_enabled, onvalue=1, offvalue=0,
                                  command=change_setting)
            lbl = tk.Label(self, text=self.name + ': ' + description)
            btn.pack(side=tk.LEFT)
            lbl.pack(side=tk.LEFT)

    class AttributeSetting(Setting):
        def __init__(self, parent, attribute_name):
            def change_attribute(now_enabled):
                Attributes.attributes[self.name].enabled = now_enabled
            super().__init__(parent, attribute_name, Attributes.attributes[attribute_name].description,
                             1 if Attributes.attributes[attribute_name].enabled else 0, change_attribute)
