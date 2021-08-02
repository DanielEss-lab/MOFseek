from MofIdentifier.DAO import SBUDAO, LigandDAO
from MofIdentifier.DAO.MOFDatabase import MOFDatabase
from MofIdentifier.DAO.DBConnection import cif_collection, ligand_collection, sbu_collection


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


def add_MOF(mof):
    _add_mof_to_collection(mof)
    for sbu in mof.sbus():
        sbu_name = SBUDAO.process_sbu(sbu, mof)
        cif_collection.update_one({"$addToSet": {"sbu_names": sbu_name}})
    ligand_names = LigandDAO.scan_all_for_mof(mof)


def _add_mof_to_collection(mof):
    file_name = mof.label
    file_name = file_name.split('.', 1)[0]
    cif_collection.update_one({"filename": file_name}, {"$set": {'cif_content': mof.file_content}})


if __name__ == "__main__":
    mof = get_MOF("ACUFEK_clean")
    print(mof)
    print(mof.cm3_g)
