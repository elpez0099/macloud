from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
import os


class GenericRepository:
    def __init__(self, collection):
        connection_string = os.environ["database_connection_string"]
        database_name = os.environ["database_name"]
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.db_collection = self.db[collection]

    def __del__(self):
        # self.client.close()
        pass

    def create(self, items):
        if isinstance(items, dict):
            self.db_collection.insert_one(items)
        elif isinstance(items, list):
            self.db_collection.insert_many(items)
        else:
            raise Exception(f'Cannot insert an item of type {type(items)}')

    def findById(self, item_id):
        print(f'buscando id: {item_id}')
        config = self.db_collection.find_one({'_id': ObjectId(item_id)})
        print(config)
        return config

    def find(self, filter):
        return self.db_collection.find(filter)

    def update(self, filter, payload):
        updated_values = {"$set": payload}
        return self.db_collection.find_one_and_update(
            filter, updated_values, return_document=ReturnDocument.AFTER)

    def delete(self, filter):
        return self.db_collection.delete_many(filter)
