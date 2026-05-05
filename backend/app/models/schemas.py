import os
from pydantic import BaseModel, Field
from typing import Optional, List

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "image_search_db")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", os.getenv("PINECONE_API", ""))
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "image-embeddings")
    GOOGLE_DRIVE_LINK = os.getenv("GOOGLE_DRIVE_LINK", "")

class UserData(BaseModel):
    phone_number: str
    image_id: Optional[str] = None
    filename: Optional[str] = None

class ImageSearchResult(BaseModel):
    id: str
    score: float
    metadata: dict = Field(default_factory=dict)

class UploadResponse(BaseModel):
    status: str
    message: str
    matches: List[ImageSearchResult] = Field(default_factory=list)
