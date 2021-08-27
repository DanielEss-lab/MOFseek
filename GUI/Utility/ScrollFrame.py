import tkinter as tk


class ScrollFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(self.parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", height=400)
        self.mofs_frame = tk.Frame(self.canvas, background="#ffffff")
        self.mofs_frame.grid_columnconfigure(0, weight=1)
        self.canvas.master = parent
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.mofs_frame, anchor="nw", tags="frame")

        self.canvas.bind('<Configure>', self.frame_width)
        self.mofs_frame.bind("<Configure>", self.on_frame_configure)
        # self.frame.bind('<Configure>', self._configure_window)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

    def frame_width(self, event):
        self.canvas.itemconfig("frame", width=self.canvas.winfo_width())

    def on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def display_results(self, results):
        self.results = results
        for widget in self.mofs_frame.winfo_children():
            widget.destroy()
        self.mofs_frame.focus_set()
        self.canvas.yview_moveto(0)
        num_shown = 0
        for mof in results:
            mof_v = MOFView.View(self.mofs_frame, mof)
            mof_v.grid(sticky=tk.EW)
            num_shown += 1
            if num_shown >= 100:
                break

    def refresh_all_attributes(self):
        for widget in self.mofs_frame.winfo_children():
            widget.refresh_attributes()

    def refresh_all_elements(self):
        for widget in self.mofs_frame.winfo_children():
            widget.refresh_elements()