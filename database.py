from pymongo import MongoClient


def get_database(name, _pass, host, app_name):
    conn_str = f"mongodb+srv://{name}:{_pass}@{host}.xnsguws.mongodb.net/?retryWrites=true&w=majority&appName={app_name}"
    client = MongoClient(conn_str)
    return client['newpBot']


def insert_new_value(collection, value_json):
    collection.insert_one(value_json)


def find_value(collection, parameter, value):
    return list(collection.find({parameter: value}))


def delete_value(collection, parameter, value):
    collection.delete_one({parameter: value})


def update_value(collection, parameter, value, new_json_value):
    collection.update_one({parameter: value}, {"$set": new_json_value})
