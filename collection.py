import IPython.parallel as parallel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_mongodb_collection():
    """
    Establish connection to MongoDB and return the relevant collection.

    Returns
    -------
    collection : pymongo.Collection
        Pymongo Collection of images and their histograms.
    """
    try:
        connection = MongoClient('localhost', 27666)
    except ConnectionFailure:
        raise Exception("Cannot instantiate ImageCollection without \
                         a MongoDB server running on port 27666")
    # return connection.image_collection.images
    return connection.image.test1


# For parallel execution, function must be in module scope

