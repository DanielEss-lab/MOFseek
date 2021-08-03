from pymongo import errors

from MofIdentifier.Molecules.SBU import SBU
from MofIdentifier.Molecules.MOF import MOF
from MofIdentifier.DAO.SBUDatabase import SBUDatabase
from MofIdentifier.DAO.DBConnection import cif_collection, ligand_collection, sbu_collection
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.subbuilding.SBUTools import SBUCollection


def get_all_names():
    try:
        names_object = sbu_collection.find({}, {"sbu_name": 1, "_id": 0})
        return list(names_object)

    except errors.OperationFailure as e:
        print("error: ", e.args)


def get_sbu(name):
    try:
        sbu_obj = sbu_collection.find_one({"sbu_name": name})
        sbu = SBUDatabase(sbu_obj["sbu_name"], sbu_obj["file_content"], sbu_obj["MOFs"])
        return sbu
    except Exception as e:
        print("error: ", e.args)


def rename_sbu(old_name, new_name):
    try:
        sbu_collection.find_one_and_update({"sbu_name": old_name}, {"$set": {"sbu_name": new_name}})
    except Exception as e:
        print("error: ", e.args)


# Returns the name, either new name because it was added or old name because it matched an existing one
def process_sbu(input_sbu, mof):
    generic_name_prefix = str(input_sbu.type)  # + '_' + str(num_type)
    highest_existing_index = -1
    for document in sbu_collection.find():
        existing_sbu = SBUDatabase(document["sbu_name"], document["file_content"], document["MOFs"])
        existing_sbu = existing_sbu.get_sbu()
        if SubGraphMatcher.match(input_sbu, existing_sbu):
            update_sbu(existing_sbu, mof)
            return existing_sbu.label
        if existing_sbu.label.startswith(generic_name_prefix):
            highest_existing_index = max(highest_existing_index, int(existing_sbu.label[len(generic_name_prefix) + 1]))
    name = generic_name_prefix + '_' + str(highest_existing_index + 1)
    add_new_sbu(input_sbu, mof, name)
    return name


def process_sbus(sbus: SBUCollection, mof):
    names = []
    for sbu in sbus.all():
        names.append(process_sbu(sbu, mof))
    return names


def update_sbu(sbu: SBU, mof_containing_it):
    sbu_collection.update_one({"sbu_name": sbu.label},
                              {"$inc": {"frequency": 1},
                               "$addToSet": {"MOFs": mof_containing_it.label}})


def add_new_sbu(sbu: SBU, first_mof_to_contain_it: MOF, name: str):
    sbu_collection.update_one({"sbu_name": name},
                              {"$set": {"file_content": sbu.file_content, "frequency": 1},
                               "$addToSet": {"MOFs": first_mof_to_contain_it.label}}, upsert=True)


if __name__ == '__main__':
    # sbu_collection.create_index("sbu_name", unique="True")
    print(*get_all_names())