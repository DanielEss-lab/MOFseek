from DAO import DBConnection, MOFDAO


def setup():
    DBConnection.use_test_connections()
    create_indices()
    # assert(MOFDAO.get_num_mofs() == 0)
    MOFDAO.add_mof()


def create_indices():
    DBConnection.mof_collection.create_index("filename", unique=True)
    DBConnection.ligand_collection.create_index("ligand_name", unique=True)
    DBConnection.sbu_collection.create_index("sbu_name", unique=True)


if __name__ == '__main__':
    setup()
