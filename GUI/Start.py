from GUI import MainWindow, DB_util
import numpy as np

if __name__ == '__main__':

    if DB_util.assert_mongod_running():
        window = MainWindow.Root()
        window.mainloop()