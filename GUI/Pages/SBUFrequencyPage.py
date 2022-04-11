import tkinter as tk

from DAOsAndServices import SBUFrequencyService
from GUI.Utility import FrameWithProcess, StyledButton

instruction_text = """Export three CSV files which contain the frequencies, sizes, and SMILES representations of SBUs 
of MOFs whose sources are currently enabled. The files (one for nodes, one for connectors, and one for auxiliary 
ligands) are output to your downloads path (see the settings page) as freq_node.csv, freq_connector.csv, and 
freq_auxiliary.csv. You can change which sources are enabled on the Settings page in order to affect the data 
output in the CSV files."""


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
