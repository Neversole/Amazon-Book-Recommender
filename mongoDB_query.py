# --------------------------------------------------------------------------------------
# This code creates our MongoDB database
# --------------------------------------------------------------------------------------

import pandas as pd
import json
from pymongo import MongoClient
import certifi


# import dnspython

def get_database():
    from pymongo import MongoClient
    import pymongo

    CONNECTION_STRING = "mongodb+srv://wsu_cpts_415:2022CPTS415@cluster0.owwy0gt.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING,
                         tlsCAFile=certifi.where())

    mydatabase = client.CPTS415_PROJECT
    collections = mydatabase.list_collection_names()
    mycollections = mydatabase.JSON

    print("List of collections", collections)

    # Create the database for our example
    return client['CPTS415_PROJECT']


if __name__ == "__main__":
    # Get the database
    dbname = get_database()
