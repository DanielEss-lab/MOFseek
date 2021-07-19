from MofIdentifier.fileIO import CifReader
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["test"]


def read_all_cifs_in_directory(cifs_path):
    # print(MOF_808.cif_content)
    print("Starting reading cif files...")
    mofs = CifReader.get_all_mofs_in_directory(cifs_path)
    print("Finished reading cif files")

    return mofs


def add_cifs_to_database(cifs_path):

    # get mofs from read all cifs in directory
    mofs = read_all_cifs_in_directory(cifs_path)

    print("Adding cif_content to database...")
    for mof in mofs:
        # Store mof data in the database using pymongo
        file_name = mof.label
        file_name = file_name.split('.', 1)[0]
        cif_collection.update_one({"filename": file_name}, {"$set": {'cif_content': mof.file_content}})
    print("Done")


if __name__ == '__main__':
    add_cifs_to_database("\\Users\\shers\\Desktop\\Chem\\test")
    # MOF = CifReader.get_mof('../mofsForTests/SOTXEG_neutral.cif')
    # cif_collection.update_one({"filename": "SOTXEG_neutral"}, {"$set": {'cif_content': MOF.cif_content}})
    # user_path = read_all_cifs_in_directory("f")
