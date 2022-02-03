import ssl

# import certifi
from pymongo import MongoClient
from GUI.DB_util import maxSevSelDelay

USE_ONLINE_SERVER = False

if USE_ONLINE_SERVER:
    cluster = MongoClient(
        "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    )  # tlsCAFile=certifi.where())
else:
    cluster = MongoClient('mongodb://localhost:27017/')
database = cluster["Database"]
mof_collection = database["mof"]
ligand_collection = database["ligand"]
sbu_collection = database["sbu"]


def use_test_connections():
    global mof_collection, ligand_collection, sbu_collection
    database = cluster["TestDatabase"]
    mof_collection = database["mof"]
    ligand_collection = database["ligand"]
    sbu_collection = database["sbu"]
