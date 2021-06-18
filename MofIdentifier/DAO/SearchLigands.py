from MofIdentifier.DAO import ReadCIFs
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader, LigandReader
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["test"]


def read_ligand(mofs, ligand_file_path):
    ligand_file = LigandReader.get_mol_from_file(ligand_file_path)
    matching_mofs = []

    for mof in mofs:
        if SubGraphMatcher.find_ligand_in_mof(ligand_file, mof):
            matching_mofs.append(mof)

    return ligand_file.label, matching_mofs


def add_ligands_to_database(ligand, matching_mofs):
    print("Start adding ligand information into database")

    for mof in matching_mofs:
        file_name = mof.label
        # mof name without .cif
        file_name = file_name.split('.', 1)[0]

        # if the cif does not have ligands field yet -> set the ligands field and value
        cif_collection.update_one({"filename": file_name}, {"$addToSet": {"ligands": ligand}})

    print("Done")


if __name__ == '__main__':
    mofs = ReadCIFs.read_all_cifs_in_directory("\\Users\\shers\\Desktop\\Chem\\test")
    ligand, matching_mofs = read_ligand(mofs,
                                        "\\Users\\shers\\Desktop\\School stuff\\Chem Lab\\Esslab-P66\\MofIdentifier\\ligands\\Benzene.txt")
    add_ligands_to_database(ligand, matching_mofs)
