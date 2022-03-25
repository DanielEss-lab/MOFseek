from DAOsAndServices import LigandDAO, MOFDAO, SBUDAO


def delete_ligand(old_name):
    LigandDAO._delete_ligand(old_name)
    MOFDAO._delete_ligand(old_name)


def delete_mof(old_name):
    sbus = MOFDAO.get_MOF(old_name).sbu_names
    MOFDAO._delete_mof(old_name)
    SBUDAO._delete_mof(old_name, sbus)


def delete_source(source_name):
    for mof in MOFDAO.get_mof_iterator():
        if source_name in mof.source_names:
            if len(mof.source_names) - 1 == 0:  # No more sources/databases for this MOF
                delete_mof(mof.filename)
            else:
                MOFDAO.remove_source(mof.filename, source_name)
