from pymongo import MongoClient
cluster = MongoClient('mongodb://localhost:27017/')
database = cluster["Database"]
mof_collection = database["mof"]


def get_all_names():
    names = list()
    names_object = mof_collection.find({}, {"filename": 1})
    for name_object in names_object:
        names.append(name_object["filename"])
    return names


for mof_name in get_all_names():
    mof_collection.update_one({"filename": mof_name}, {"$unset": {"source_name": []}})
    mof_collection.update_one({"filename": mof_name}, {"$set": {"source_names": []}})
    mof_collection.update_one({"filename": mof_name}, {"$addToSet": {'source_names': "2019-11-01-ASR-public_12020/structure_10143"}})
