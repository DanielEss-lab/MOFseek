from MofIdentifier.DAO import ReadCIFs
from MofIdentifier.DAO.MOFDatabase import MOFDatabase
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader, LigandReader
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["test"]


def read_ligand(ligand_file_path):
    ligand_file = LigandReader.get_mol_from_file(ligand_file_path)
    mofs_from_database = []
    matched_mofs = []

    for document in cif_collection.find():
        mof = MOFDatabase(document)
        mofs_from_database.append(mof)

    for mof in mofs_from_database:
        if mof.cif_content is not None:
            if SubGraphMatcher.find_ligand_in_mof(ligand_file, mof.get_mof()):
                matched_mofs.append(mof)

    return ligand_file.label, matched_mofs


def add_ligands_to_database(ligand, matched_mofs):
    print("Start adding ligand information into database")

    for mof in matched_mofs:
        # if the cif does not have ligands field yet -> set the ligands field and value
        cif_collection.update_one({"filename": mof.filename}, {"$addToSet": {"ligand_names": ligand}})

    print("Done")


if __name__ == '__main__':
    # mofs = ReadCIFs.read_all_cifs_in_directory("\\Users\\shers\\Desktop\\Chem\\test") ligand, matching_mofs =
    # read_ligand(mofs, "\\Users\\shers\\Desktop\\School stuff\\Chem
    # Lab\\Esslab-P66\\MofIdentifier\\ligands\\Benzene.txt") add_ligands_to_database(ligand, matching_mofs)

    ligand, matched_mofs = read_ligand(
        "\\Users\\shers\\Desktop\\School stuff\\Chem Lab\\Esslab-P66\\MofIdentifier\\ligands\\Benzene.smiles")
    add_ligands_to_database(ligand, matched_mofs)
