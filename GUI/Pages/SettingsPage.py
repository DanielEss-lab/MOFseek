import platform
import tkinter as tk
import tkinter.ttk as ttk

from GUI import Attributes, Settings
from GUI.Utility import StyledButton
from GUI.Utility.ScrollFrame import ScrollFrame

instruction_text = """Select which properties you would like to search by and see for each MOF. """


class Page(ScrollFrame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.frame = self.get_frame()
        instructions = tk.Label(self.frame, text=instruction_text, justify=tk.LEFT)
        instructions.grid()
        for attr in Attributes.attributes:
            Page.AttributeSetting(self.frame, attr).grid(sticky=tk.W)

        Page.Setting(self.frame, 'SBU search', 'Enable the powerful (but situational) SBU search', 0,
                     lambda enabled: self.winfo_toplevel().toggle_sbu_search(enabled)).grid(sticky=tk.W, pady=(20, 0))

        def solvent_button_action(enabled):
            Settings.toggle_solvent(enabled)
            self.winfo_toplevel().toggle_solvent()
        Page.Setting(self.frame, 'Keep Solvent', 'Export and view any solvent molecules that were in the original file '
                                                 'along with the MOF itself', Settings.keep_solvent,
                     solvent_button_action).grid(sticky=tk.W, pady=(20, 0))

        def disorder_button_action(enabled):
            Settings.toggle_disorder(enabled)
            self.winfo_toplevel().forget_history()
        Page.Setting(self.frame, 'Allow Disorder', 'Include in results MOFs that have been marked DISORDER for '
                                                   'containing illogical structures (Only affects future searches)',
                     Settings.allow_disorder, disorder_button_action).grid(sticky=tk.W, pady=(20, 2))

        def allow_not_organic_action(enabled):
            Settings.toggle_allow_not_organic(enabled)
            self.winfo_toplevel().forget_history()
        Page.Setting(self.frame, 'Allow Inorganic', 'Include in search results "MOFs" that do not contain carbon '
                                                    'and/or hydrogen (Only affects future searches)',
                     Settings.allow_not_organic, allow_not_organic_action).grid(sticky=tk.W, pady=(2, 0))

        def allow_no_metal_action(enabled):
            Settings.toggle_allow_no_metal(enabled)
            self.winfo_toplevel().forget_history()
        Page.Setting(self.frame, 'Allow Nonmetallic', 'Include in search results MOFs that do not contain metal nodes '
                                                      '(ie COFs) (Only affects future searches)',
                     Settings.allow_no_metal, allow_no_metal_action).grid(sticky=tk.W, pady=(2, 20))

        self.download_filepath_option_row = self.make_download_filepath_option_row()
        self.download_filepath_option_row.grid(sticky=tk.W, pady=(0, 2))

        self.app_select_labels = {".cif": None, ".xyz": None, ".smiles": None}
        for extension in self.app_select_labels:
            app_select_row, self.app_select_labels[extension] = self.make_app_select_option_row(extension)
            app_select_row.grid(sticky=tk.W, pady=(0, 2))

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

    def make_download_filepath_option_row(self):
        row = tk.Frame(self.frame)

        def callback():
            Settings.change_download_filepath()
            self.refresh_download_filepath_row()

        btn = StyledButton.make(row, 'Change filepath to save molecules onto computer in order to open',
                                command=callback)
        lbl = tk.Label(row, text=Settings.download_filepath)
        btn.pack(side=tk.LEFT)
        lbl.pack(side=tk.LEFT)
        return row

    def make_app_select_option_row(self, file_extension):
        row = tk.Frame(self.frame)
        if self.app_select_labels[file_extension] is None:
            text = Settings.open_app_filepath[file_extension]
            if text == "":
                text = "<computer default for this filetype>"
            lbl = tk.Label(row, text=text)
        else:
            lbl = self.app_select_labels[file_extension]

        def callback():
            try:
                Settings.change_app_filepath(file_extension)
                lbl['text'] = Settings.open_app_filepath[file_extension]
            except ValueError:
                if platform.system() == 'Darwin':
                    lbl['text'] = "Error; reverting to computer default. On Macs, you can specify the filepath to " \
                                  "the executable within a .app package by using command-shift-G within the app " \
                                  "select menu"
                else:
                    lbl['text'] = "Error; reverting to computer default. Make sure you use the true full path to the " \
                                  "executable file"

        btn = StyledButton.make(row, f'Specify application (full filepath) to use when opening {file_extension} files',
                                command=callback)
        btn.pack(side=tk.LEFT)
        lbl.pack(side=tk.LEFT)
        return row, lbl

    def refresh_download_filepath_row(self):
        self.download_filepath_option_row.grid_forget()
        self.download_filepath_option_row = self.make_download_filepath_option_row()
        self.download_filepath_option_row.grid(sticky=tk.W)