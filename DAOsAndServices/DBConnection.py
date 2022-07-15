import ssl

# import certifi
from pymongo import MongoClient
from GUI.DB_util import maxSevSelDelay

USE_ONLINE_SERVER = False

if USE_ONLINE_SERVER:
    cluster = MongoClient(
        "mongodb+srv:/* insert db link here */retryWrites=true&w=majority",
    )  # tlsCAFile=certifi.where())
else:
    cluster = MongoClient('mongodb://localhost:27017/')
database = cluster["Database"]
mof_collection = database["mof"]
ligand_collection = database["ligand"]
sbu_collection = database["sbu"]


def use_test_connections():
    global database, mof_collection, ligand_collection, sbu_collection
    database = cluster["TestDatabase"]
    mof_collection = database["mof"]
    ligand_collection = database["ligand"]
    sbu_collection = database["sbu"]
