import tkinter as tk


class ScrollFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(self.parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", height=400)
        self.content_frame = tk.Frame(self.canvas, background="#ffffff")
        self.canvas.master = parent
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.content_frame, anchor="nw", tags="frame")

        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig("frame", width=self.canvas.winfo_width()))
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>",
                         lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def get_frame(self):
        return self.content_frame
