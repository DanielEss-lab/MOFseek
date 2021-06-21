from tkinter import *
import tkinter.ttk as ttk
import threading
import time

class Main_Frame(object):
    def __init__(self, top=None):
        # save root reference
        self.top = top
        # set title bar
        self.top.title("Loading bar example")

        # start button calls the "initialization" function bar_init, you can pass a variable in here if desired
        self.start_button = ttk.Button(top, text='Start bar', command=lambda: self.bar_init(2500))
        self.start_button.pack()

        # the progress bar will be referenced in the "bar handling" and "work" threads
        self.load_bar = ttk.Progressbar(top)
        self.load_bar.pack()

        # run mainloop
        self.top.mainloop()

    def bar_init(self, var):
        # first layer of isolation, note var being passed along to the self.start_bar function
        # target is the function being started on a new thread, so the "bar handler" thread
        self.start_bar_thread = threading.Thread(target=self.start_bar, args=(var,))
        # start the bar handling thread
        self.start_bar_thread.start()

    def start_bar(self, var):
        # the load_bar needs to be configured for indeterminate amount of bouncing
        self.load_bar.config(mode='indeterminate', maximum=100, value=0)
        # 8 here is for speed of bounce
        self.load_bar.start(64)
        # start the work-intensive thread, again a var can be passed in here too if desired
        self.work_thread = threading.Thread(target=self.work_task, args=(var,))
        self.work_thread.start()
        # close the work thread
        self.work_thread.join()
        # stop the indeterminate bouncing
        self.load_bar.stop()
        # reconfigure the bar so it appears reset
        self.load_bar.config(value=0, maximum=0)

    def work_task(self, wait_time):
        for x in range(wait_time):
           time.sleep(0.001)

if __name__ == '__main__':
    # create root window
    root = Tk()
    # call Main_Frame class with reference to root as top
    Main_Frame(top=root)