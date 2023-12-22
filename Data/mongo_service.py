import pymongo

active_book: pymongo.collection = None
client = None
offline_book: [] = None


def get_client_connection():
    global client
    client = pymongo.MongoClient() # enter here uri
    return client


def load_book(collection_name):
    global active_book
    active_book = client['Chess_opening_trainer'][collection_name]
    restore_book()


def update_book():
    active_book.delete_many({})
    active_book.insert_many(offline_book)


def restore_book():
    global offline_book
    if offline_book is None: offline_book = []
    else: offline_book.clear()
    for x in active_book.find():
        offline_book.append(x)
