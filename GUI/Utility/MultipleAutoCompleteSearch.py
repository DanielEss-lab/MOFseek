import tkinter as tk

from GUI.Utility import AutoCompleteComboBox


class View(tk.Frame):
    def __init__(self, parent, focus_function=None, font=("Arial", 10)):
        self.font = font
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        self.focus_function = focus_function
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.initial_combobox = AutoCompleteComboBox.Box(self, self.font, focus_function)
        self.initial_combobox.grid(row=0, column=1, pady=2, sticky=tk.NSEW)
        if focus_function is not None:
            self.focus_button_by_row_index = dict()
            initial_focus_button = tk.Button(self, text='i', font=('Consolas', self.font[1]),
                                             command=lambda: focus_function(self.initial_combobox.get()))
            initial_focus_button.grid(row=0, column=2, pady=2)
        self.box_by_row_index = dict()
        self.minus_button_by_row_index = dict()
        self.values = None
        second_row_button = tk.Button(self, text='+', font=self.font, command=lambda: self.new_combobox(second_row_button))
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
        for button in self.minus_button_by_row_index.values():
            self.remove_combobox(button)
        self.focus_button_by_row_index = dict()
        self.minus_button_by_row_index = dict()
        self.box_by_row_index = dict()
        self.initial_combobox.delete(0, tk.END)

    def new_combobox(self, button):
        row_index = button.grid_info()['row']
        button['text'] = '-'
        button['command'] = lambda: self.remove_combobox(button)
        self.minus_button_by_row_index[row_index] = button

        combobox = AutoCompleteComboBox.Box(self, self.font, self.focus_function)
        combobox.set_completion_list(self.values)
        self.box_by_row_index[row_index] = combobox
        combobox.grid(row=row_index, column=1, pady=2, sticky=tk.NSEW)
        combobox.focus_set()
        if self.focus_function is not None:
            focus_button = tk.Button(self, text='i', font=('Consolas', self.font[1]),
                                     command=lambda: self.focus_function(combobox.get()))
            self.focus_button_by_row_index[row_index] = focus_button
            focus_button.grid(row=row_index, column=2, pady=2)
        new_row_button = tk.Button(self, text='+', font=self.font, command=lambda: self.new_combobox(new_row_button))
        new_row_button.grid(row=row_index+1, column=0, pady=2)

    def remove_combobox(self, button):
        row_index = button.grid_info()['row']
        button.grid_forget()
        combobox = self.box_by_row_index[row_index]
        combobox.delete(0, tk.END)
        combobox.grid_forget()
        self.focus_button_by_row_index[row_index].grid_forget()

    def add_new_possible_value(self, label):
        self.values.append(label)
        self.set_possible_values(self.values)


if __name__ == '__main__':
    root = tk.Tk(className=' AutocompleteEntry demo')
    MACS = View(root)
    test_list = ['apple', 'banana', 'CranBerry', 'dogwood', 'alpha', 'Acorn', 'Anise']
    MACS.set_possible_values(test_list)
    MACS.pack()
    root.bind('<Control-q>', lambda event=None: root.destroy())
    root.mainloop()
