import os
import tkinter.filedialog as fd
from tkinter import messagebox
import shelve

from GUI import Attributes

with shelve.open("MOFseek_settings") as s:
    download_filepath = s.get("download_path", "")
    open_app_filepath = {".xyz": s.get("open.xyz", ""),
                         ".smiles": s.get("open.smiles", ""),
                         ".cif": s.get("open.cif", "")}
    keep_solvent = s.get("keep_solvent", True)
    allow_disorder = s.get("allow_disorder", False)
    allow_not_organic = s.get("allow_not_organic", True)
    allow_no_metal = s.get("allow_no_metal", False)
    use_sbu_search = s.get("use_sbu_search", False)
    attribute_is_enabled = dict()
    for name, attr in Attributes.attributes.items():
        attribute_is_enabled[name] = s.get(name, attr.enabled)


def change_download_filepath():
    global download_filepath
    download_filepath = fd.askdirectory()
    if download_filepath is None or not os.path.isdir(download_filepath):
        change_download_filepath()
    else:
        with shelve.open("MOFseek_settings", 'w') as shelf:
            shelf["download_path"] = download_filepath


def get_download_filepath():
    global download_filepath
    if os.path.isdir(download_filepath):
        return download_filepath
    else:
        messagebox.showinfo("Requires Filepath", "To show the file, the application requires a filepath in which it "
                                                 "can place a file for you to view. Please select that location in "
                                                 "the prompt that will appear when you hit 'okay'.")
        change_download_filepath()
        return get_download_filepath()


def change_app_filepath(file_extension):
    global open_app_filepath
    open_app_filepath[file_extension] = fd.askopenfilename()
    if open_app_filepath[file_extension] is None or os.path.isdir(open_app_filepath[file_extension]):
        open_app_filepath[file_extension] = ""
        raise ValueError('Invalid path to an app. Make sure you use the full path to the executable file')
    else:
        with shelve.open("MOFseek_settings", 'w') as shelf:
            shelf["open" + file_extension] = open_app_filepath[file_extension]


def toggle_attribute_display(attribute_name, enabled):
    global attribute_is_enabled
    attribute_is_enabled[attribute_name] = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf[attribute_name] = enabled


def toggle_solvent(enabled):
    global keep_solvent
    keep_solvent = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf["keep_solvent"] = keep_solvent


def toggle_disorder(enabled):
    global allow_disorder
    allow_disorder = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf["allow_disorder"] = allow_disorder


def toggle_allow_not_organic(enabled):
    global allow_not_organic
    allow_not_organic = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf["allow_not_organic"] = allow_not_organic


def toggle_allow_no_metal(enabled):
    global allow_no_metal
    allow_no_metal = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf["allow_no_metal"] = allow_no_metal


def toggle_sbu(enabled):
    global use_sbu_search
    use_sbu_search = enabled
    with shelve.open("MOFseek_settings", 'w') as shelf:
        shelf["use_sbu_search"] = use_sbu_search