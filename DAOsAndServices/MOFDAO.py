import csv

from DAOsAndServices import SBUDAO, LigandDAO
from DAOsAndServices.MOFDatabase import MOFDatabase
from DAOsAndServices.DBConnection import mof_collection
from MofIdentifier.subbuilding.SBUIdentifier import NoMetalsException


def get_MOF(name):
    if name.endswith('.cif'):
        name = name[:-4]
    mof = mof_collection.find_one({"filename": name})
    return None if mof is None else MOFDatabase(mof)


def get_all_names():
    names = list()
    names_object = mof_collection.find({}, {"filename": 1})
    for name_object in names_object:
        names.append(name_object["filename"])
    return names


def get_mof_iterator():
    cursor = mof_collection.find({})
    generator = (MOFDatabase(mof_dict) for mof_dict in cursor)
    return generator


def get_passing_MOFs(search):
    results = []
    for document in mof_collection.find():
        mof = MOFDatabase(document)
        if search.passes(mof):
            results.append(mof)
    return results


def add_mof(mof, source_name):
    mof_name = _add_mof_to_collection(mof, source_name)
    try:
        for sbu in mof.sbus().clusters:
            sbu_name = SBUDAO.process_sbu(sbu, mof_name)
            sbu_freq = sbu.frequency # How many times the SBU appears in that MOF
            sbu_connectivity = sbu.connections()
            sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
            mof_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_node_info": sbu_info}})
        for sbu in mof.sbus().connectors:
            sbu_name = SBUDAO.process_sbu(sbu, mof_name)
            sbu_freq = sbu.frequency
            sbu_connectivity = sbu.connections()
            sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
            mof_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_conn_info": sbu_info}})
        for sbu in mof.sbus().auxiliaries:
            sbu_name = SBUDAO.process_sbu(sbu, mof_name)
            sbu_freq = sbu.frequency
            sbu_connectivity = sbu.connections()
            sbu_info = str(sbu_freq) + ' ' + str(sbu_connectivity) + ' ' + sbu_name
            mof_collection.update_one({"filename": mof_name}, {"$addToSet": {"sbu_aux_info": sbu_info}})
    except NoMetalsException:
        pass
    LigandDAO.scan_all_for_mof(mof)


def _add_mof_to_collection(mof, source_name):
    mof_name = mof.label
    if mof_name.endswith('.cif'):
        mof_name = mof_name[:-4]
    mof_collection.update_one({"filename": mof_name}, {"$set": {'cif_content': mof.file_content,
                                                                'calculated_info': mof.get_calculated_info_string(),
                                                                "sbu_node_info": [],
                                                                "sbu_conn_info": [],
                                                                "sbu_aux_info": [],
                                                                "source_names": []}}, upsert=True)
    add_source_to_mof(mof_name, source_name)
    return mof_name


def _rename_ligand(old_name, new_name):
    mof_collection.update_many({"ligand_names": old_name}, {"$set": {"ligand_names.$": new_name}})
    # TODO: test that this actually works


def _delete_ligand(old_name):
    mof_collection.update_many({}, {"$pull": {"ligand_names": old_name}})
    # TODO: test that this actually works


def _rename_sbu(old_name, new_name, sbu_type):
    mof_collection.update_many({"ligand_names": old_name}, {"$set": {"ligand_names.$": new_name}})
    # TODO: test that this actually works
    array_name = array_name_of_type(sbu_type)
    for document in mof_collection.find():
        sbu_infos = document[array_name]
        for sbu_info in sbu_infos:
            name = sbu_info[sbu_info.rindex(' '):]
            if name == old_name:
                correct_sbu_info = sbu_info[0:1 + sbu_info.rindex(' ')] + new_name
                mof_collection.update_one({"_id": document["_id"], array_name: sbu_info},
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
        for row in csv_file:
            items = dict(row)
            if '' in items:
                items.pop('')
            name = items['filename']
            mof_collection.find_one_and_update({"filename": name}, {"$set": items})


if __name__ == "__main__":
    mof = get_MOF("ACUFEK_clean")
    print(mof)
    print(mof.cm3_g)


def delete_all_mofs():
    mof_collection.delete_many({})


def get_num_mofs():
    return mof_collection.count()


def _delete_mof(name):
    mof_collection.delete_one({"filename": name})


def remove_source(mof_name, source_name):
    mof_collection.update_one({"filename": mof_name}, {"$pull": {'source_names': source_name}})


def add_source_to_mof(mof_name, source_name):
    mof_collection.update_one({"filename": mof_name}, {"$addToSet": {'source_names': source_name}})


if __name__ == "__main__":
    mof_collection.update_one({"filename": "ABAVIJ_clean"}, {"$addToSet": {'source_names': "first one"}})
