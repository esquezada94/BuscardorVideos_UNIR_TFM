import chromadb
from chromadb.api.types import Where

def init_chroma(collection_name):
    database_directory = f'./databases'
    client_chroma = chromadb.PersistentClient(path=database_directory)
    collections = [i.name for i in client_chroma.list_collections()]
    if collection_name in collections:
        collection = client_chroma.get_collection(collection_name)
    else:
        collection = client_chroma.create_collection(collection_name)
    
    # Contar todos los elementos en la colección
    total_count = collection.count()
    print(f"Total de elementos en la colección: {total_count}")
    return collection

def save_data_chroma(collection, list_ids, list_text, metadata):
    collection.add(
        documents = list_text,
        metadatas = metadata,
        ids = list_ids
    )
    return collection.count()

def search_chroma(collection, query, filters, top):
    results = collection.query(
        query_texts = query,
        where = filters,
        n_results = top,
        include=["embeddings", "metadatas", "documents"]
    )
    return results

def delete_from_chroma(collection, filter: dict):
    collection.delete(where=filter)
    print(f"Registros eliminados.")