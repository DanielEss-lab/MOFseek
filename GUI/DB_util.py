import pymongo as pm
import tkinter as tk
from pymongo.errors import ServerSelectionTimeoutError

maxSevSelDelay = 1


def assert_mongod_running():
    try:
        client = pm.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=maxSevSelDelay)
        client.server_info()
        return True
    except ServerSelectionTimeoutError:
        window = tk.Tk()
        tk.Label(window, text='This application requires the mongod or MongoDB process (eg MongoDB Community Server) '
                              'to be running,\nwhich can be installed from '
                              'https://www.mongodb.com/try/download/community?tck=docs_server . '
                              '\nIt is recommended to install as a service.\n\n Please install and/or start'
                              'the process, then retry opening this app.', justify=tk.LEFT).pack()
        window.mainloop()
        return False


if __name__ == '__main__':
    assert_mongod_running()