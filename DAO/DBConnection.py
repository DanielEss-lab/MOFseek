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
cif_collection = database["test_"]
ligand_collection = database["test_ligands_"]
sbu_collection = database["test_sbus_"]