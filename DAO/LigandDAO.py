from DAO.LigandDatabase import LigandDatabase
from DAO.MOFDatabase import MOFDatabase
from DAO.DBConnection import mof_collection, ligand_collection
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader


def add_ligand_to_db(ligand):
    ligand_for_db = _read_ligand(ligand)
    try:
        ligand_collection.update_one({"ligand_name": ligand_for_db.name},
                                     {"$set": {"ligand_file_content": ligand_for_db.file_content},
                                      "$addToSet": {"MOFs": {"$each": ligand_for_db.Mofs}}}, upsert=True)
    except Exception as e:
        print("error: ", e.args)


def get_ligand_iterator():
    cursor = ligand_collection.find({})
    generator = (LigandDatabase.from_dict(ligand_dict) for ligand_dict in cursor)
    return generator


def add_ligand_to_db_from_filepath(ligand_file_path):
    ligand_file = LigandReader.get_mol_from_file(ligand_file_path)
    add_ligand_to_db(ligand_file)


def _read_ligand(ligand_file):
    matched_mof_names = []
    # i = 0
    for document in mof_collection.find():
        mof = MOFDatabase(document)
        if mof.file_content is not None:
            if SubGraphMatcher.find_ligand_in_mof(ligand_file, mof.get_mof()):
                # i += 1
                matched_mof_names.append(mof.filename)
                mof_collection.update_one({"filename": mof.filename}, {"$addToSet": {"ligand_names": ligand_file.label}})
    # print(f"{ligand_file.label} found in {i} mofs")
    ligand_for_database = LigandDatabase(ligand_file.label, ligand_file.file_content, matched_mof_names)

    return ligand_for_database


def _delete_ligand(old_name):
    ligand_collection.delete_one({"ligand_name": old_name})


def get_all_names():
    names = list()
    try:
        ligand_names_object = ligand_collection.find({}, {"ligand_name": 1, "_id": 0})
        for ligand_names in ligand_names_object:
            names.append(ligand_names["ligand_name"])
    except Exception as e:
        print("error: ", e.args)
    return names


def get_ligand(ligand_name):
    try:
        ligand_obj = ligand_collection.find_one({"ligand_name": ligand_name})
        # ligand = ligand_collection.find({}, {"ligand_name": ligand_name, "_id": 0})
        ligand = LigandDatabase.from_dict(ligand_obj)
        return ligand
    except Exception as e:
        print("error: ", e.args)


def _rename_ligand(old_name, new_name):
    try:
        ligand_collection.find_one_and_update({"ligand_name": old_name}, {"$set": {"ligand_name": new_name}})
    except Exception as e:
        print("error: ", e.args)


def scan_all_for_mof(mof):
    ligands = []
    for ligand in ligand_collection.find():
        ligand = LigandDatabase.from_dict(ligand)
        if SubGraphMatcher.find_ligand_in_mof(ligand.get_ligand(), mof):
            mof_name = mof.label
            if mof_name.endswith('.cif'):
                mof_name = mof_name[:-4]
            ligand_collection.update_one({"ligand_name": ligand.name}, {"$addToSet": {"MOFs": mof_name}})
            mof_collection.update_one({"filename": ligand.name}, {"$addToSet": {"ligand_names": mof_name}})
            ligands.append(ligand.name)
    return ligands


def delete_all_ligands():
    ligand_collection.delete_many({})


def delete_unmatched_ligands():
    ligand_collection.delete_many({"MOFs": {"$exists": True, "$size": 0}})


if __name__ == '__main__':
    # --worked--
    # ligand, matched_mofs, ligand_for_db = read_ligand(
    #     "\\Users\\shers\\Desktop\\School stuff\\Chem Lab\\Esslab-P66\\MofIdentifier\\ligands\\Benzene.smiles")
    # add_ligands_to_database(ligand, matched_mofs)
    # add_ligand_info_to_ligand_collection(ligand_for_db)

    # --worked--
    # search_all_ligand_names()
    print(get_ligand("Benzene.smiles"))
    # rename_ligand("hi.smiles", "Benzene.smiles")

