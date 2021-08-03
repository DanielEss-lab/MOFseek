from MofIdentifier.DAO.LigandDatabase import LigandDatabase
from MofIdentifier.DAO.MOFDatabase import MOFDatabase
from MofIdentifier.DAO.DBConnection import cif_collection, ligand_collection, sbu_collection
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader


def add_ligand_to_db(ligand):
    ligand_name, matched_mofs, ligand_for_db = read_ligand(ligand)
    update_mof_collection(ligand_name, matched_mofs)
    update_ligand_collection(ligand_for_db)


def add_ligand_to_db_from_filepath(ligand_file_path):
    ligand_file = LigandReader.get_mol_from_file(ligand_file_path)
    add_ligand_to_db(ligand_file)


def read_ligand(ligand_file):
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


def update_mof_collection(ligand, matched_mofs):
    for mof in matched_mofs:
        # if the cif does not have ligands field yet -> set the ligands field and value
        cif_collection.update_one({"filename": mof.filename}, {"$addToSet": {"ligand_names": ligand}})


def update_ligand_collection(ligand_for_db: LigandDatabase):
    try:
        ligand_collection.update_one({"ligand_name": ligand_for_db.ligand_name},
                                     {"$set": {"ligand_file_content": ligand_for_db.ligand_file},
                                      "$addToSet": {"MOFs": {"$each": ligand_for_db.Mofs}}}, upsert=True)
    except Exception as e:
        print("error: ", e.args)


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
        ligand = LigandDatabase(ligand_obj["ligand_name"], ligand_obj["ligand_file_content"], ligand_obj["MOFs"])
        return ligand
    except Exception as e:
        print("error: ", e.args)


def rename_ligand(old_name, new_name):
    try:
        ligand_collection.find_one_and_update({"ligand_name": old_name}, {"$set": {"ligand_name": new_name}})
    except Exception as e:
        print("error: ", e.args)


def scan_all_for_mof(mof):
    for ligand in cif_collection.find():
        if SubGraphMatcher.find_ligand_in_mof(ligand, mof):
            ligand_collection.update_one({"ligand_name": ligand.label}, {"$addToSet": {"MOFs": mof.label}})
            cif_collection.update_one({"filename": ligand.label}, {"$addToSet": {"ligand_names": mof.label}})


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

