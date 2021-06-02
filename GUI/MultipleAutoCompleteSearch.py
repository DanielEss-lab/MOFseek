import tkinter as tk

from GUI import AutoCompleteComboBox


class View(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, height=400, width=800, bd=2, relief=tk.SOLID)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.initial_combobox = AutoCompleteComboBox.Box(self)
        self.initial_combobox.grid(row=0, column=1, pady=2, sticky=tk.NSEW)
        self.box_by_row_index = dict()
        self.values = None
        second_row_button = tk.Button(self, text='+', command=lambda: self.new_combobox(second_row_button))
        second_row_button.grid(row=1, column=0, pady=2)

    def get_values(self):
        values = [box.get() for box in self.box_by_row_index.values()] + [self.initial_combobox.get()]
        return [value for value in values if value is not None and value != '']

    def set_possible_values(self, values):
        self.values = values
        for box in self.box_by_row_index.values():
            box.set_completion_list(values)
        self.initial_combobox.set_completion_list(values)

    def clear(self):
        for box in self.box_by_row_index.values():
            box.delete(0, tk.END)
        self.initial_combobox.delete(0, tk.END)

    def new_combobox(self, button):
        button['text'] = '-'
        button['command'] = lambda: self.remove_combobox(button)

        row_index = button.grid_info()['row']
        combobox = AutoCompleteComboBox.Box(self)
        combobox.set_completion_list(self.values)
        self.box_by_row_index[row_index] = combobox
        combobox.grid(row=row_index, column=1, pady=2, sticky=tk.NSEW)
        combobox.focus_set()

        new_row_button = tk.Button(self, text='+', command=lambda: self.new_combobox(new_row_button))
        new_row_button.grid(row=row_index+1, column=0, pady=2)

    def remove_combobox(self, button):
        row_index = button.grid_info()['row']
        button.grid_forget()
        combobox = self.box_by_row_index[row_index]
        combobox.delete(0, tk.END)
        combobox.grid_forget()

    def add_new_possible_value(self, label):
        self.set_possible_values(self.values.extend(label))


if __name__ == '__main__':
    root = tk.Tk(className=' AutocompleteEntry demo')
    MACS = View(root)
    test_list = ['apple', 'banana', 'CranBerry', 'dogwood', 'alpha', 'Acorn', 'Anise' ]
    MACS.set_possible_values(test_list)
    MACS.pack()
    root.bind('<Control-q>', lambda event=None: root.destroy())
    root.mainloop()
