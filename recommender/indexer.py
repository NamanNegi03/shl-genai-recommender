import json
import chromadb
from sentence_transformers import SentenceTransformer
import os

def build_vector_store():
    # Assuming this script is run from the root directory (SHL_project)
    data_path = "data/raw_assessments.json"
    persist_directory = "data/chroma_db"
    
    os.makedirs(persist_directory, exist_ok=True)

    print("Initializing ChromaDB client...")
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Reset collection if you run this multiple times
    try:
        client.delete_collection(name="shl_assessments")
    except Exception:
        pass
        
    collection = client.create_collection(name="shl_assessments")
    
    print("Loading SentenceTransformer model (this will download ~80MB the first time)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Loading data from {data_path}...")
    with open(data_path, 'r') as f:
        assessments = json.load(f)
        
    documents = []
    metadatas = []
    ids = []
    
    print("Encoding documents into vectors...")
    for i, item in enumerate(assessments):
        # We craft a specific string for the AI to "read" and embed
        doc_text = f"Assessment Name: {item['name']}. Type: {', '.join(item['test_type'])}. {item['description']}"
        documents.append(doc_text)
        
        # Flatten the list into a string for ChromaDB compatibility
        flat_metadata = {
            "name": item["name"],
            "url": item["url"],
            "description": item["description"],
            "duration": item["duration"],
            "adaptive_support": item["adaptive_support"],
            "remote_support": item["remote_support"],
            "test_type": ", ".join(item["test_type"]) 
        }
        metadatas.append(flat_metadata)
        ids.append(str(i))
        
    embeddings = model.encode(documents).tolist()
    
    print("Saving to vector database...")
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Vector database built successfully! Check the data/chroma_db folder.")

if __name__ == "__main__":
    build_vector_store()