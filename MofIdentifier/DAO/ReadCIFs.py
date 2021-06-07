from MofIdentifier.fileIO import CifReader
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["CIFs"]


def read_all_cifs_in_directory(cifs_path):
    # MOF_808 = CifReader.get_mof('../mofsForTests/smod7-pos-1.cif')
    # print(MOF_808.cif_content)
    print("Starting reading cif files...")
    mofs = CifReader.get_all_mofs_in_directory(cifs_path)
    print("Finished reading cif files")

    print("Adding cif_content to database...")
    for mof in mofs:
        # Store mof data in the database using pymongo
        file_name = mof.label
        file_name = file_name.split('.', 1)[0]
        cif_collection.update_one({"filename": file_name}, {"$set": {'cif_content': mof.cif_content}})
    print("Done")


if __name__ == '__main__':
    read_all_cifs_in_directory("\\Users\\shers\\Desktop\\Chem\\structure_10143")
    # user_path = read_all_cifs_in_directory("f")
