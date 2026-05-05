from motor.motor_asyncio import AsyncIOMotorClient
from app.models.schemas import Config

class MongoService:
    def __init__(self):
        self.uri = Config.MONGO_URI
        self.db_name = Config.MONGO_DB_NAME
        self.client = None
        self.db = None
        
    def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            print(f"Connected to MongoDB at {self.uri}")

    def close(self):
        if self.client:
            self.client.close()

    async def save_user_data(self, phone_number: str, image_id: str, filename: str):
        if self.db is None:
            self.connect()
            
        collection = self.db["users"]
        doc = {
            "phone_number": phone_number,
            "image_id": image_id,
            "filename": filename
        }
        
        try:
            result = await collection.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return None

mongo_service = MongoService()
