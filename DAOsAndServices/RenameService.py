from DAOsAndServices import LigandDAO, MOFDAO, SBUDAO


def rename_ligand(old_name, new_name):
    LigandDAO._rename_ligand(old_name, new_name)
    MOFDAO._rename_ligand(old_name, new_name)

def rename_sbu(old_name, new_name, type):
    SBUDAO._rename_sbu(old_name, new_name)
    MOFDAO._rename_sbu(old_name, new_name, type)