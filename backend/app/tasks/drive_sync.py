import os
import glob
import uuid
import gdown
from PIL import Image
from app.models.schemas import Config
from app.services.clip_service import clip_service
from app.services.pinecone_service import pinecone_service

DOWNLOAD_DIR = "downloaded_images"

def sync_drive_images():
    print("Starting Drive Sync Cron Job...")
    link = Config.GOOGLE_DRIVE_LINK
    
    if not link:
        print("GOOGLE_DRIVE_LINK is not set. Skipping sync.")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    try:
        # Assuming link is a public folder link
        print(f"Downloading from {link}...")
        try:
            gdown.download_folder(link, output=DOWNLOAD_DIR, quiet=True, use_cookies=True)
        except Exception as gdown_e:
            print(f"gdown encountered an issue (likely rate limits), but will process what we have. Error: {gdown_e}")
            
        # Process downloaded images
        image_files = []
        for ext in ('*.png', '*.jpg', '*.jpeg'):
            image_files.extend(glob.glob(os.path.join(DOWNLOAD_DIR, '**', ext), recursive=True))
            
        print(f"Found {len(image_files)} images to process.")
        
        # Load already processed filenames
        processed_file = os.path.join(DOWNLOAD_DIR, "processed.txt")
        processed = set()
        if os.path.exists(processed_file):
            with open(processed_file, "r") as f:
                processed = set(f.read().splitlines())
        
        for file_path in image_files:
            try:
                # generate a unique id for the image
                image_id = str(uuid.uuid4())
                filename = os.path.basename(file_path)
                
                if filename in processed:
                    continue
                
                print(f"Processing image {filename}...")
                
                # generate embedding
                img = Image.open(file_path)
                embedding = clip_service.generate_embedding(img)
                
                # store in pinecone
                success = pinecone_service.upsert_embedding(
                    image_id=image_id,
                    embedding=embedding,
                    metadata={"filename": filename, "source": "google_drive"}
                )
                
                if success:
                    print(f"Successfully synced {filename}")
                    # Mark as processed
                    with open(processed_file, "a") as f:
                        f.write(filename + "\n")
                    processed.add(filename)
                else:
                    print(f"Failed to upsert {filename}")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
        print("Drive Sync completed.")
        
    except Exception as e:
        print(f"Drive sync failed: {e}")
