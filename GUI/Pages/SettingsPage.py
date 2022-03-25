import platform
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from DAOsAndServices import DeleteService
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

        def sbu_button_action(enabled):
            Settings.toggle_sbu(enabled)
            self.winfo_toplevel().toggle_sbu_search(enabled)
        Page.Setting(self.frame, 'SBU search', 'Enable the powerful (but situational) SBU search',
                     Settings.use_sbu_search, sbu_button_action).grid(sticky=tk.W, pady=(20, 0))

        def solvent_button_action(enabled):
            Settings.toggle_solvent(enabled)
            self.winfo_toplevel().toggle_solvent()
        Page.Setting(self.frame, 'Keep Solvent', 'Export and view any solvent molecules that were in the original file '
                                                 'along with the MOF itself', Settings.keep_solvent,
                     solvent_button_action).grid(sticky=tk.W, pady=(20, 0))

        def disorder_button_action(enabled):
            Settings.toggle_disorder(enabled)
            self.winfo_toplevel().forget_history()
            self.winfo_toplevel().clear_search()
        Page.Setting(self.frame, 'Allow Disorder', 'Include in results MOFs that have been marked DISORDER for '
                                                   'containing illogical structures (Only affects future searches)',
                     Settings.allow_disorder, disorder_button_action).grid(sticky=tk.W, pady=(20, 2))

        def allow_not_organic_action(enabled):
            Settings.toggle_allow_not_organic(enabled)
            self.winfo_toplevel().forget_history()
            self.winfo_toplevel().clear_search()
        Page.Setting(self.frame, 'Allow Inorganic', 'Include in search results "MOFs" that do not contain carbon '
                                                    'and/or hydrogen (Only affects future searches)',
                     Settings.allow_not_organic, allow_not_organic_action).grid(sticky=tk.W, pady=(2, 0))

        def allow_no_metal_action(enabled):
            Settings.toggle_allow_no_metal(enabled)
            self.winfo_toplevel().forget_history()
            self.winfo_toplevel().clear_search()
        Page.Setting(self.frame, 'Allow Nonmetallic', 'Include in search results MOFs that do not contain metal nodes '
                                                      '(ie COFs) (Only affects future searches)',
                     Settings.allow_no_metal, allow_no_metal_action).grid(sticky=tk.W, pady=(2, 20))
        instructions = tk.Label(self.frame, text="Choose which databases to enable", justify=tk.LEFT)
        instructions.grid()
        self.sources_frame = tk.Frame(self.frame)
        self.remake_sources_frame_children()

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
                Settings.toggle_attribute_display(attribute_name, now_enabled)

            super().__init__(parent, attribute_name, Attributes.attributes[attribute_name].description,
                             1 if Settings.attribute_is_enabled[attribute_name] else 0, change_attribute)

    class SourceSetting(tk.Frame):
        def __init__(self, parent, source_name, is_enabled):
            self.parent = parent
            self.name = source_name
            super().__init__(self.parent)
            self.is_enabled = tk.IntVar(value=1 if is_enabled else 0)

            btn = ttk.Checkbutton(self, variable=self.is_enabled, onvalue=1, offvalue=0,
                                  command=self.change_setting)
            lbl = tk.Label(self, text=self.name + ': ' + f"Show results tagged with this source name.")
            delete = StyledButton.make(self, text=f"Delete", command=self.delete_source)
            btn.pack(side=tk.LEFT)
            lbl.pack(side=tk.LEFT)
            delete.pack(side=tk.LEFT)

        def change_setting(self):
            now_enabled = self.is_enabled.get()
            Settings.toggle_source(self.name, now_enabled)
            self.toggle_sources_in_views(now_enabled)

        def delete_source(self):
            if messagebox.askquestion("Confirm source deletion", "Deleting this source will also delete from the "
                                                                 "database all MOFs that are associated with only this "
                                                                 "source name. This cannot be automatically undone."
                                                                 " Are you sure you want to proceed?"):
                Settings.delete_source_name(self.name)
                DeleteService.delete_source(self.name)
                if self.is_enabled.get():
                    self.toggle_sources_in_views(False)
                self.parent.winfo_toplevel().update_sources_settings()

        def toggle_sources_in_views(self, now_enabled):
            self.winfo_toplevel().reload_sbus()
            self.winfo_toplevel().refresh_mol_views()
            self.winfo_toplevel().clear_search()
            self.winfo_toplevel().forget_history()

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

    def remake_sources_frame_children(self):
        for child in self.sources_frame.winfo_children():
            child.destroy()
        for source_name, is_enabled in Settings.current_source_states().items():
            Page.SourceSetting(self.sources_frame, source_name, is_enabled).grid(sticky=tk.W)
        self.sources_frame.grid(sticky=tk.W, pady=(2, 20))
        return self.sources_frame

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
        self.download_filepath_option_row.grid(sticky=tk.W, pady=(0,2))
