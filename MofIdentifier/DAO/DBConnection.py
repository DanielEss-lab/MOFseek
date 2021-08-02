import certifi
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
database = cluster["Database"]
cif_collection = database["test"]
ligand_collection = database["test_ligands"]
sbu_collection = database["test_sbus"]