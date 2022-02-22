from DAOsAndServices.DBConnection import mof_collection


def store_value(mof_name, attribute_name, value):
    mof_collection.update_one({"filename": mof_name}, {"$set": {attribute_name: value}})
