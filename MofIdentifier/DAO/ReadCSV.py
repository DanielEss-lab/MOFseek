import pymongo
import csv
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://db_admin:EHfbvgmVEJ9g0Mgk@cluster0.r0otj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = cluster["Database"]
cif_collection = database["CIFs"]


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
