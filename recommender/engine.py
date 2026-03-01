import chromadb
from sentence_transformers import SentenceTransformer
# --- ADD THIS PATCH AT THE VERY TOP ---
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# --------------------------------------



class RecommendationEngine:
    def __init__(self, db_path="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(name="shl_assessments")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    # ... rest of your code ...
        
    def recommend(self, query: str, top_k: int = 10):
        # 1. Embed the user's text query
        query_embedding = self.model.encode([query]).tolist()
        
        # 2. Search ChromaDB for the closest vector matches
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        raw_recommendations = results['metadatas'][0]
        
        # 3. Format the results back into exactly what the API expects
        final_recs = []
        for rec in raw_recommendations:
            # Reconstruct the test_type list from the comma-separated string
            test_type_str = rec.get("test_type", "")
            test_type_list = [t.strip() for t in test_type_str.split(",")] if test_type_str else []
            
            final_recs.append({
                "name": rec.get("name"),
                "url": rec.get("url"),
                "description": rec.get("description"),
                "duration": int(rec.get("duration", 30)),
                "adaptive_support": rec.get("adaptive_support"),
                "remote_support": rec.get("remote_support"),
                "test_type": test_type_list
            })
            
        return final_recs