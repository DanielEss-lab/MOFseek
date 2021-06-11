import tkinter as tk
import tkinter.ttk as ttk
import traceback

from GUI import UploadLigandView, FrameWithProcess
from GUI.Search import TerminableThread

instruction_text = """Choose from your computer a .xyz file or a .txt file whose first line is a SMILES string. It will 
be loaded onto the database and added to the ligand list of all MOFs that contain it. The calculations will take some 
time (expect 20-60 minutes), so please be patient."""


class AddLigandPage(FrameWithProcess.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        instructions = tk.Label(self, text=instruction_text, justify=tk.LEFT)
        instructions.pack()
        self.upload_ligand_v = UploadLigandView.View(self)
        self.upload_ligand_v.pack()
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.btn_cancel = tk.Button(self, text="Cancel", command=self.cancel_process)

        self.error_row = tk.Frame(self)
        self.exit_error_btn = tk.Button(self.error_row, text='X', command=self.exit_error)
        self.exit_error_btn.pack(side=tk.LEFT)
        self.lbl_error_text = tk.Label(self.error_row, fg='red')
        self.lbl_error_text.pack(side=tk.LEFT)

    def start_process(self, mol):
        def process():
            try:
                self.progress.start()
                self.winfo_toplevel().add_custom_ligand(mol)
            except InterruptedError:
                pass
            except Exception as ex:
                error_text = traceback.format_exc()
                self.show_error(ex)
                print(error_text)
            finally:
                self.progress.stop()
                self.progress.pack_forget()
                self.btn_cancel.pack_forget()

        self.progress.pack(fill=tk.X)
        self.btn_cancel.pack()
        self.thread = TerminableThread.ThreadWithExc(target=process)
        self.thread.start()

    def cancel_process(self):
        try:
            self.thread.raiseExc(InterruptedError)
        except AssertionError as e:
            print(e)
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_cancel.pack_forget()

    def show_error(self, error):
        self.lbl_error_text['text'] = 'Error: ' + str(error)
        self.error_row.pack()

    def exit_error(self):
        self.error_row.pack_forget()
