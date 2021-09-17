from DAO import LigandDAO, MOFDAO, SBUDAO


def delete_ligand(old_name):
    LigandDAO._delete_ligand(old_name)
    MOFDAO._delete_ligand(old_name)
