import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askopenfilenames

from DAOsAndServices.MOFDatabase import MOFDatabase
from GUI.Utility import FrameWithProcess, StyledButton
from GUI.Views import MultiMofView
from DAOsAndServices import MOFDAO
from MofIdentifier.fileIO import CifReader

instruction_text = """Choose one or more .cif files from your computer. The MOFs will be read and they will show up 
here. The calculations will take some time (expect 15 seconds per MOF for this step), so please be patient."""


class Page(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, lambda _: self.open_mofs())
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        open_btn = StyledButton.make(self, text='Open Mof(s)', command=lambda: self.start_process())
        open_btn.pack()
        self.mof_preview = MultiMofView.View(self)
        self.mof_preview.pack(fill=tk.X)

    def open_mofs(self, *args):
        filenames = askopenfilenames(filetypes=[('CIF Files', '*.cif')])
        mofs = []
        if filenames is not None and len(filenames) > 0:
            for filename in filenames:
                try:
                    mof = CifReader.get_mof(str(Path(filename)))
                    mofs.append(mof)
                except:
                    self._show_error('Unable to extract MOF from ' + filename)
                    return
        self.parent.mofs = mofs
        mofs_for_display = [MOFDatabase.from_mof(mof) for mof in mofs]
        self.mof_preview.display_results(mofs_for_display)
        if len(mofs) > 0:
            self.parent.enable_store_button()

    def refresh_attributes_shown(self):
        self.mof_preview.display_results(self.parent.mofs)

    def empty_display(self):
        self.mof_preview.display_results([])
