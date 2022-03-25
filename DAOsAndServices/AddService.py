from DAOsAndServices import MOFDAO


def add_mofs(mofs, source_name):
    for mof in mofs:
        add_mof(mof, source_name)


def add_mof(mof, source_name):
    existing_mof = MOFDAO.get_MOF(mof.label)
    if existing_mof is None:
        MOFDAO.add_mof(mof, source_name)
    else:
        if existing_mof.get_mof().near_equals(mof):
            MOFDAO.add_source_to_mof(existing_mof.filename, source_name)
        else:
            mof.label = mof.label + "-" + source_name
            MOFDAO.add_mof(mof, source_name)
