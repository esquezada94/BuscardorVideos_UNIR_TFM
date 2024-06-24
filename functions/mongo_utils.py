import pymongo

client = pymongo.MongoClient("mongodb://host.docker.internal:27017/", serverSelectionTimeoutMS=30000, socketTimeoutMS=None, connectTimeoutMS=30000)  
#client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=30000, socketTimeoutMS=None, connectTimeoutMS=30000)  

def init_mongodb(db_name, collection_name):
    db = client[db_name]
    collection = db.get_collection(collection_name)

    return collection

def save_mongodb(collection, data):
    # Insertar el documento
    resultado = collection.insert_one(data)

    # Imprimir el ID del documento insertado
    print("Documento insertado con ID:", resultado.inserted_id)

def query_mongodb(collection, filter):
    cursor = collection.find(filter)
    list_documents = []
    # Iterar sobre los resultados e imprimirlos
    for document in cursor:
        list_documents.append(document)

    return list_documents

def delete_mongodb(collection, filter):
    result = collection.delete_many(filter)

    return result.deleted_count

def aggregate_mongodb(collection, filter):
    cursor = collection.aggregate(filter)
    list_documents = []
    # Iterar sobre los resultados e imprimirlos
    for document in cursor:
        list_documents.append(document)

    return list_documents