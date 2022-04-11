import tkinter as tk

from GUI import os_specific_settings


class HorizontalScrollFrame(tk.Frame):
    def __init__(self, parent, height, *args, **kwargs):
        self.parent = parent
        super().__init__(self.parent, height=height, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.master = parent
        self.content_frame = tk.Frame(self.canvas)
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hsb.set)

        self.hsb.pack(side="bottom", fill="x", expand=False)
        self.canvas.pack(side="top", fill="x", expand=False)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", tags="frame")

        # self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig("frame", height=self.canvas.winfo_height()))
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.size_frame()

    def get_frame(self):
        return self.content_frame

    def size_frame(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update()
        self.canvas.configure(height=self.content_frame.winfo_height())

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        self.size_frame()

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        self.size_frame()
