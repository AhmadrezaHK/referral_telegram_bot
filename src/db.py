import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")

# mydict = {"name": "John", "address": "Highway 37"}

# x = col.insert_one(mydict)

# print(x.inserted_id)


db = client["yekbot"]

col = db["candidates"]


def insertDB(document):
    col.insert_one(document)
