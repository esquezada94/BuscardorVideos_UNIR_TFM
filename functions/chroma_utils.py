import chromadb

def init_chroma(database_name, collection_name):
    database_directory = f'./{database_name}'
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

def save_data_chroma(collection, list_ids, list_text, list_embeddings, metadata):
    if list_embeddings:
        collection.add(
            documents = list_text,
            embeddings = list_embeddings,
            metadatas = metadata,
            ids = list_ids
        )
    else:
        collection.add(
            documents = list_text,
            metadatas = metadata,
            ids = list_ids
        )
    
    return collection.count()

def search_chroma(collection, query_text, query_embedding, filters, top):
    if query_text:
        results = collection.query(
            query_texts = query_text,
            where = filters,
            n_results = top,
            include=["embeddings", "metadatas", "documents", "distances"]
        )
    else:
        results = collection.query(
            query_embeddings = query_embedding,
            where = filters,
            n_results = top,
            include=["embeddings", "metadatas", "documents", "distances"]
        )
    return results

def delete_from_chroma(collection, filter: dict):
    collection.delete(where=filter)
    print(f"Registros eliminados.")