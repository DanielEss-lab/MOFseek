import certifi as certifi

from MofIdentifier.DAO import ReadCIFs
from MofIdentifier.DAO.LigandDatabase import LigandDatabase
from MofIdentifier.DAO.MOFDatabase import MOFDatabase
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader, LigandReader
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
database = cluster["Database"]
cif_collection = database["test"]
ligand_collection = database["test_ligands"]


def add_ligand_to_db_from_file(ligand_file_path):
    ligand, matched_mofs, ligand_for_db = read_ligand(ligand_file_path)
    add_ligands_to_database(ligand, matched_mofs)
    add_ligand_info_to_ligand_collection(ligand_for_db)


def read_ligand(ligand_file_path):
    ligand_file = LigandReader.get_mol_from_file(ligand_file_path)
    mofs_from_database = []
    matched_mofs = []
    matched_mof_names = []

    for document in cif_collection.find():
        mof = MOFDatabase(document)
        mofs_from_database.append(mof)

    for mof in mofs_from_database:
        if mof.file_content is not None:
            if SubGraphMatcher.find_ligand_in_mof(ligand_file, mof.get_mof()):
                matched_mofs.append(mof)
                matched_mof_names.append(mof.filename)

    ligand_for_database = LigandDatabase(ligand_file.label, ligand_file.file_content, matched_mof_names)

    return ligand_file.label, matched_mofs, ligand_for_database


def add_ligands_to_database(ligand, matched_mofs):
    print("Start adding ligand information into database")

    for mof in matched_mofs:
        # if the cif does not have ligands field yet -> set the ligands field and value
        cif_collection.update_one({"filename": mof.filename}, {"$addToSet": {"ligand_names": ligand}})

    print("Done")


def add_ligand_info_to_ligand_collection(ligand_for_db: LigandDatabase):
    print("Start adding ligand information into Ligand Collection")
    ligand_collection.create_index("ligand_name", unique="True")
    # TODO: try this code without the above line, to see if it still enforces no-duplicates
    try:
        ligand_collection.update_one({"ligand_name": ligand_for_db.ligand_name},
                                     {"$set": {"ligand_file_content": ligand_for_db.ligand_file},
                                      "$addToSet": {"MOFs": {"$each": ligand_for_db.Mofs}}}, upsert=True)
    except Exception as e:
        print("error: ", e.args)

    print("Done")


def search_all_ligand_names():
    print("This is the all ligand names list from database:")
    names = list()
    try:
        ligand_names_object = ligand_collection.find({}, {"ligand_name": 1, "_id": 0})
        for ligand_names in ligand_names_object:
            names.append(ligand_names["ligand_name"])
    except Exception as e:
        print("error: ", e.args)
    return names


def search_specific_ligand_by_name(ligand_name):
    print("This is the data of", ligand_name, ":")

    try:
        ligand_obj = ligand_collection.find_one({"ligand_name": ligand_name})
        # ligand = ligand_collection.find({}, {"ligand_name": ligand_name, "_id": 0})
        ligand = LigandDatabase(ligand_obj["ligand_name"], ligand_obj["ligand_file_content"], ligand_obj["MOFs"])
        return ligand
    except Exception as e:
        print("error: ", e.args)


if __name__ == '__main__':

    # --worked--
    # ligand, matched_mofs, ligand_for_db = read_ligand(
    #     "\\Users\\shers\\Desktop\\School stuff\\Chem Lab\\Esslab-P66\\MofIdentifier\\ligands\\Benzene.smiles")
    # add_ligands_to_database(ligand, matched_mofs)
    # add_ligand_info_to_ligand_collection(ligand_for_db)

    # --worked--
    # search_all_ligand_names()
    search_specific_ligand_by_name("Benzene.smiles")
