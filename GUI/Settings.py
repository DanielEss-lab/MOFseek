import os
import tkinter.filedialog as fd
from tkinter import messagebox

download_filepath = ""
keep_solvent = True
allow_disorder = False
allow_not_organic = False
allow_no_metal = False
# TODO: use borg instead of global variables
# Attribute related settings are stored in Attributes


def change_download_filepath():
    global download_filepath
    download_filepath = fd.askdirectory()
    if download_filepath is None or not os.path.isdir(download_filepath):
        change_download_filepath()


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


def toggle_solvent(enabled):
    global keep_solvent
    keep_solvent = enabled


def toggle_disorder(enabled):
    global allow_disorder
    allow_disorder = enabled


def toggle_allow_not_organic(enabled):
    global allow_not_organic
    allow_not_organic = enabled


def toggle_allow_no_metal(enabled):
    global allow_no_metal
    allow_no_metal = enabled