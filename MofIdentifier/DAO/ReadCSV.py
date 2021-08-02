import csv
from MofIdentifier.DAO.DBConnection import cif_collection, ligand_collection, sbu_collection


def read_CSV():
    # total: 12020 files
    with open("2019-11-01-ASR-public_12020.csv", 'r') as file:
        csv_files = csv.DictReader(file)
        for row in csv_files:
            cif_collection.create_index("filename", unique="True")
            try:
                cif_collection.insert_one(dict(row))
            except Exception as e:
                print(e.args, "Should have thrown a mongo write exception due to duplicate key")
        print("Done")


if __name__ == '__main__':
    read_CSV()
    # post = {"_id": 0, "name": "hi"}
    # collection.insert_one(post)
