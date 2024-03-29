from MofIdentifier.Molecules.SBU import SBU
from DAOsAndServices.SBUDatabase import SBUDatabase
from DAOsAndServices.DBConnection import sbu_collection
from MofIdentifier.SubGraphMatching import SubGraphMatcher


def get_all_names():
    names = list()
    try:
        names_object = sbu_collection.find({}, {"sbu_name": 1, "_id": 0})
        for name in names_object:
            names.append(name["sbu_name"])
    except Exception as e:
        print("error: ", e.args)
    return names


def get_sbu(name):
    if name.endswith('.xyz'):
        name = name[:-4]
    try:
        sbu_obj = sbu_collection.find_one({"sbu_name": name})
        sbu = SBUDatabase(sbu_obj["sbu_name"], sbu_obj["file_content"], sbu_obj["MOFs"], sbu_obj["type"])
        return sbu
    except Exception as e:
        print("error: ", e.args)


def get_sbu_iterator():
    cursor = sbu_collection.find({})
    generator = (SBUDatabase(sbu_obj["sbu_name"], sbu_obj["file_content"], sbu_obj["MOFs"], sbu_obj["type"])
                 for sbu_obj in cursor)
    return generator


def _rename_sbu(old_name, new_name):
    try:
        sbu_collection.find_one_and_update({"sbu_name": old_name}, {"$set": {"sbu_name": new_name}})
    except Exception as e:
        print("error: ", e.args)


# Returns the name, either new name because it was added or old name because it matched an existing one
def process_sbu(input_sbu, mof_name):
    generic_name_prefix = str(input_sbu.type)  # + '_' + str(num_type)
    highest_existing_index = -1
    for document in sbu_collection.find():
        existing_sbu = SBUDatabase(document["sbu_name"], document["file_content"], document["MOFs"], document["type"])
        if str(input_sbu.type) != existing_sbu.type:
            continue
        existing_sbu = existing_sbu.get_sbu()
        if SubGraphMatcher.match(input_sbu, existing_sbu):
            update_sbu(existing_sbu, mof_name)
            return existing_sbu.label[:-4] if existing_sbu.label.endswith('.xyz') else existing_sbu.label
        # Same type sbus, but different structures, then we get the index on name, so that we can make a new name:
        if existing_sbu.label.startswith(generic_name_prefix):
            existing_sbu_index = existing_sbu.label[len(generic_name_prefix) + 1:]
            if existing_sbu_index.endswith('.xyz'):
                existing_sbu_index = existing_sbu_index[:-4]
            highest_existing_index = max(highest_existing_index, int(existing_sbu_index))
    # The code reaches here unless it found a match
    name = generic_name_prefix + '_' + str(highest_existing_index + 1)
    add_new_sbu(input_sbu, mof_name, name)
    return name


def process_sbus(sbus, mof_name):
    names = []
    for sbu in sbus:
        names.append(process_sbu(sbu, mof_name))
    return names


def update_sbu(sbu: SBU, mof_name):
    label: str = sbu.label
    if label.lower().endswith('.xyz'):
        label = sbu.label[:-4]
    else:
        label = sbu.label
    sbu_collection.update_one({"sbu_name": label},
                              {"$inc": {"frequency": 1},
                               "$addToSet": {"MOFs": mof_name}})


def add_new_sbu(sbu: SBU, mof_name, name: str):
    sbu_collection.update_one({"sbu_name": name, "type": str(sbu.type)},
                              {"$set": {"file_content": sbu.file_content, "frequency": 1},
                               "$addToSet": {"MOFs": mof_name}}, upsert=True)


def delete_all_sbus():
    sbu_collection.delete_many({})


if __name__ == '__main__':
    # sbu_collection.create_index("sbu_name", unique="True")
    print(*get_all_names())


def get_num_sbus():
    return sbu_collection.count()


def _delete_mof(mof_name, sbu_names):
    sbu_collection.update_many({}, {"$pull": {"MOFs": mof_name}})
    for sbu_name in sbu_names:
        if len(get_sbu(sbu_name).mofs) == 0:
            sbu_collection.delete_one({"sbu_name": sbu_name})
