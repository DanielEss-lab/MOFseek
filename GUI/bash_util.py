import subprocess
from pathlib import Path

import pymongo as pm
from pymongo.errors import ServerSelectionTimeoutError

maxSevSelDelay = 1


def run_mongod():
    try:
        client = pm.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=maxSevSelDelay)
        client.server_info()
    except ServerSelectionTimeoutError as err:
        subprocess.run([str(Path('./run_mongod.sh'))], shell=True)
        print('Attempted to start MobgoDB process')


def stop_mongod():
    try:
        client = pm.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=maxSevSelDelay)
        client.server_info()
        # client[db_name].eval("db.shutdownServer()")
    except ServerSelectionTimeoutError as err:
        return
    subprocess.run([str(Path(r'./stop_mongod.sh'))], shell=True)


if __name__ == '__main__':
    stop_mongod()