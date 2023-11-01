from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.exceptions import MongoDBConnectionException, MongoDBOperationException


class MongoDBConnection():

    def __init__(self, config: dict):
        self.mongodb_config = config['mongo_db']
        self.uri = f"mongodb+srv://{self.mongodb_config['user']}:{self.mongodb_config['pwd']}@{self.mongodb_config['cluster']}.rbhmf4q.mongodb.net/?retryWrites=true&w=majority"
        self.client = None

    def get_client(self, is_recreation=False) -> MongoClient:
        # Create a new client and connect to the server
        print("Creating Mongo client")
        if not self.client or is_recreation:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return self.client
        except Exception as e:
            print(e)
            raise MongoDBConnectionException(e)

    def insert_data(self, data_dict) -> int:
        try:
            print("Getting cluster")
            self.get_client()
            database = self.client.Cluster0
            print("Getting database activities")
            print(data_dict)
            activities_collection = database['activities']
            result = activities_collection.insert_many(data_dict)
            print("I inserted %x documents." % (len(result.inserted_ids)))
            return len(result.inserted_ids)
        except Exception as e:
            print(e)
            raise MongoDBOperationException(e)
