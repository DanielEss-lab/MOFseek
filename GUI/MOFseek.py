import numpy
from GUI import MainWindow, DB_util

if __name__ == '__main__':

    if DB_util.assert_mongod_running():
        window = MainWindow.Root()
        window.mainloop()