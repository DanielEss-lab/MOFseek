import csv

from DAO import SBUDAO, LigandDAO
from DAO.MOFDatabase import MOFDatabase
from DAO.DBConnection import cif_collection


def get_MOF(name):
    if name.endswith('.cif'):
        name = name[:-4]
    mof = cif_collection.find_one({"filename": name})

    return MOFDatabase(mof)


def get_all_names():
    names = list()
    names_object = cif_collection.find({}, {"filename": 1})
    for name_object in names_object:
        names.append(name_object["filename"])
    return names


def get_passing_MOFs(search):
    results = []
    for document in cif_collection.find():
        mof = MOFDatabase(document)
        if search.passes(mof):
            results.append(mof)
    return results


def add_mof(mof):
    mof_name = _add_mof_to_collection(mof)
    for sbu in mof.sbus().clusters:
        sbu_name = SBUDAO.process_sbu(sbu, mof_name)
        sbu_freq = sbu.frequency
        sbu_connectivity = sbu.connections()
        sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
        cif_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_node_info": sbu_info}})
    for sbu in mof.sbus().connectors:
        sbu_name = SBUDAO.process_sbu(sbu, mof_name)
        sbu_freq = sbu.frequency
        sbu_connectivity = sbu.connections()
        sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
        cif_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_conn_info": sbu_info}})
    for sbu in mof.sbus().auxiliaries:
        sbu_name = SBUDAO.process_sbu(sbu, mof_name)
        sbu_freq = sbu.frequency
        sbu_connectivity = sbu.connections()
        sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
        cif_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_aux_info": sbu_info}})
    LigandDAO.scan_all_for_mof(mof)


def store_value(mof_name, attribute_name, value):
    cif_collection.update_one({"filename": mof_name}, {"$set": {attribute_name: value}})


def _add_mof_to_collection(mof):
    mof_name = mof.label
    if mof_name.endswith('.cif'):
        mof_name = mof_name[:-4]
    cif_collection.update_one({"filename": mof_name}, {"$set": {'cif_content': mof.file_content,
                                                                "sbu_node_info": [],
                                                                "sbu_conn_info": [],
                                                                "sbu_aux_info": []}}, upsert=True)
    return mof_name


def _rename_ligand(old_name, new_name):
    cif_collection.update_many({"ligand_names": old_name}, {"$set": {"ligand_names.$": new_name}})
    # TODO: test that this actually works


def _rename_sbu(old_name, new_name, sbu_type):
    cif_collection.update_many({"ligand_names": old_name}, {"$set": {"ligand_names.$": new_name}})
    # TODO: test that this actually works
    array_name = array_name_of_type(sbu_type)
    for document in cif_collection.find():
        sbu_infos = document[array_name]
        for sbu_info in sbu_infos:
            name = sbu_info[sbu_info.rindex(' '):]
            if name == old_name:
                correct_sbu_info = sbu_info[0:1 + sbu_info.rindex(' ')] + new_name
                cif_collection.update_one({"_id": document["_id"], array_name: sbu_info},
                                          {"$set": {array_name + '.$': correct_sbu_info}})


def array_name_of_type(sbu_type):
    if sbu_type == 'cluster':
        return 'sbu_node_info'
    elif sbu_type == 'connector':
        return 'sbu_conn_info'
    else:
        return 'sbu_aux_info'


def add_csv_info(csv_file_path):
    with open(csv_file_path, 'r') as file:
        csv_file = csv.DictReader(file)
        i = 0
        for row in csv_file:
            if i % 10 == 0:
                print(i)
            i += 1
            items = dict(row)
            if '' in items:
                items.pop('')
            name = items['filename']
            cif_collection.find_one_and_update({"filename": name}, {"$set": items})


if __name__ == "__main__":
    mof = get_MOF("ACUFEK_clean")
    print(mof)
    print(mof.cm3_g)


def delete_all_mofs():
    cif_collection.delete_many({})


def get_num_mofs():
    return cif_collection.count()
