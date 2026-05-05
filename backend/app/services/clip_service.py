from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch
import io
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.mtcnn = None
        self.resnet = None
        self.is_loaded = False

    def load_model(self):
        if not self.is_loaded:
            print(f"Loading FaceNet model on {self.device}...")
            # MTCNN for face detection and cropping
            self.mtcnn = MTCNN(keep_all=False, device=self.device)
            # InceptionResnetV1 for generating face embeddings (512 dimensions)
            self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            self.is_loaded = True
            print("FaceNet model loaded.")

    def generate_embedding(self, image: Image.Image) -> list[float]:
        self.load_model()
        # Convert image to RGB if not already
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Detect and crop face
        face = self.mtcnn(image)
        
        # If no face is detected, we return a zero vector or handle it
        if face is None:
            print("WARNING: No face detected in image. Returning zero vector.")
            return [0.0] * 512
            
        # Ensure it's a batch of 1
        if face.dim() == 3:
            face = face.unsqueeze(0)
            
        face = face.to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            embedding = self.resnet(face)
            
        # Normalize the embedding using L2 normalization
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.squeeze(0).cpu().tolist()

    def generate_embedding_from_bytes(self, image_bytes: bytes) -> list[float]:
        image = Image.open(io.BytesIO(image_bytes))
        return self.generate_embedding(image)

# We'll keep the object name clip_service to avoid breaking imports in main.py and drive_sync.py
clip_service = EmbeddingService()
