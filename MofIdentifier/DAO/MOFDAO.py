from pymongo import MongoClient

from MofIdentifier.DAO.MOFDatabase import MOFDatabase

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["test"]


def get_MOF(name):
    mof = cif_collection.find_one({"filename": name})

    return MOFDatabase(mof)


def get_passing_MOFs(search):
    results = []
    for document in cif_collection.find():
        mof = MOFDatabase(document)
        if search.passes(mof):
            results.append(mof)
    return results


if __name__ == "__main__":
    mof = get_MOF("ACUFEK_clean")
    print(mof)
    print(mof.cm3_g)
