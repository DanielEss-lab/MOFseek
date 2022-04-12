import tkinter as tk

from DAOsAndServices import SBUFrequencyService
from GUI.Utility import FrameWithProcess, StyledButton

instruction_text = """Create nine files with information about the SBUs 
of MOFs whose sources are currently enabled. The files (three for nodes, three for connectors, and three for auxiliary 
ligands) are output to your downloads path (see the settings page) as freq_{node, connector, or auxiliary}.csv, 
freq_{node, connector, or auxiliary}_w_images.xlsx, and freq_{node, connector, or auxiliary}_w_issues.csv. Each type of
SBU has three files. One file contains the frequencies, sizes, and SMILES representations of each unit; one file contains
that and their images, but only for atoms whose images can be generated from the SMILES; one file contains only those units for which 
the image could not be generated. You can change which sources are enabled on the 
Settings page in order to affect the data output in the CSV files."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, self.export_files)
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.add_btn = StyledButton.make(self, 'Export', lambda: self.start_process())
        self.add_btn.pack()

    def export_files(self, *args):
        SBUFrequencyService.export_sbus()
