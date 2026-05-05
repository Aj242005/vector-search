from pinecone import Pinecone, ServerlessSpec
from app.models.schemas import Config

class PineconeService:
    def __init__(self):
        self.api_key = Config.PINECONE_API_KEY
        self.index_name = Config.PINECONE_INDEX_NAME
        self.pc = None
        self.index = None
        self.dimension = 512 # CLIP model output dimension
        
        if self.api_key:
            self.pc = Pinecone(api_key=self.api_key)
            self._ensure_index()
            
    def _ensure_index(self):
        if not self.pc:
            return
            
        try:
            existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1") # default spec
                )
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")

    def upsert_embedding(self, image_id: str, embedding: list[float], metadata: dict = None):
        if not self.index:
            print("Pinecone index not initialized.")
            return False
            
        try:
            self.index.upsert(
                vectors=[
                    {"id": image_id, "values": embedding, "metadata": metadata or {}}
                ]
            )
            return True
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")
            return False

    def search_similar(self, embedding: list[float], top_k: int = 5, threshold: float = 0.50) -> list[dict]:
        if not self.index:
            print("Pinecone index not initialized.")
            return []
            
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            matches = []
            for match in results.get("matches", []):
                # Filter by 50% threshold
                if match.get("score", 0) >= threshold:
                    matches.append({
                        "id": match["id"],
                        "score": match["score"],
                        "metadata": match.get("metadata", {})
                    })
            return matches
        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            return []

pinecone_service = PineconeService()
