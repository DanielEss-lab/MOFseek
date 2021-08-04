from pymongo import MongoClient

from GUI import DB_util

cat_before = {'name': 'Whiskers', 'color': 'calico', 'personality': 'bold'}
cat_middle = {'name': 'Void', 'color': 'black', 'personality': 'cuddly'}
cat_after = {'name': 'Spook', 'color': 'grey', 'personality': 'lethal'}


DB_util.run_mongod()

client = MongoClient('mongodb://localhost:27017/')
database = client.test_database
collection = database['scratch_paper_cats']
collection.insert_one(cat_middle)
print(list(collection.find()))
DB_util.stop_mongod('scratch_paper_cats')
collection.insert_one(cat_after)