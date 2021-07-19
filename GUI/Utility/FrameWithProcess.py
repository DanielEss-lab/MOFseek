import tkinter as tk
import tkinter.ttk as ttk
import traceback

from GUI import os_specific_settings
from GUI.Utility import TerminableThread, StyledButton


class Frame(tk.Frame):
    def __init__(self, parent, process, **args):
        self.process = process
        tk.Frame.__init__(self, parent, **args)

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='indeterminate')

        self.btn_cancel = StyledButton.make(self, text="Cancel", command=self._cancel_process)

        self.error_row = tk.Frame(self)
        self.exit_error_btn = StyledButton.make(self.error_row, text='X', command=self._hide_error)
        self.exit_error_btn.pack(side=tk.LEFT)
        self.lbl_error_text = tk.Label(self.error_row, fg='red')
        self.lbl_error_text.pack(side=tk.LEFT)
        self.process_is_going = False

    def add_error_to_layout(self, error_row):
        error_row.pack()

    def add_progress_to_layout(self, progress):
        progress.pack(fill=tk.X)

    def add_cancel_to_layout(self, btn_cancel):
        btn_cancel.pack()

    def start_process(self, arg=None):
        if self.process_is_going:
            self._cancel_process()

        def process():
            try:
                self.progress.start(os_specific_settings.PROGRESS_SPEED)
                self.process_is_going = True
                self.process(arg)
            except InterruptedError:
                pass
            except Exception as ex:
                error_text = traceback.format_exc()
                self._show_error(ex)
                print(error_text)
            finally:
                self.process_is_going = False
                self.progress.stop()
                self.progress.pack_forget()
                self.btn_cancel.pack_forget()
                self.progress.grid_forget()
                self.btn_cancel.grid_forget()

        self.add_progress_to_layout(self.progress)
        self.add_cancel_to_layout(self.btn_cancel)
        self.thread = TerminableThread.ThreadWithExc(target=process)
        self.thread.start()

    def _cancel_process(self):
        try:
            self.thread.raiseExc(InterruptedError)
        except AssertionError as e:
            print(e)
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_cancel.pack_forget()
        self.progress.grid_forget()
        self.btn_cancel.grid_forget()

    def _show_error(self, error):
        self.lbl_error_text['text'] = 'Error: ' + str(error)
        self.add_error_to_layout(self.error_row)

    def _hide_error(self):
        self.error_row.pack_forget()
        self.error_row.grid_forget()
