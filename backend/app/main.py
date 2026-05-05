from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io
import zipfile
import os
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import uuid

from dotenv import load_dotenv
load_dotenv()

from app.services.clip_service import clip_service
from app.services.pinecone_service import pinecone_service
from app.services.mongo_service import mongo_service
from app.tasks.drive_sync import sync_drive_images
from app.models.schemas import UploadResponse

# Scheduler
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up application...")
    
    # Init Mongo connection
    mongo_service.connect()
    
    # Start Cron Job
    scheduler.add_job(sync_drive_images, 'date')
    scheduler.add_job(sync_drive_images, 'interval', minutes=5)
    scheduler.start()
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    scheduler.shutdown()
    mongo_service.close()

app = FastAPI(title="Image Similarity Platform", lifespan=lifespan)

# Mount downloaded images directory so frontend can display them
os.makedirs("downloaded_images", exist_ok=True)
app.mount("/images", StaticFiles(directory="downloaded_images"), name="images")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "Status": 200,
        "Message": "The System is working fine"
    }

@app.get("/download/{filename}")
async def download_single(filename: str):
    file_path = os.path.join("downloaded_images", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

@app.post("/upload", response_model=UploadResponse)
async def upload_image(
    phone_number: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Read image
        image_bytes = await file.read()
        
        # Generate embedding
        print(f"Generating embedding for upload by {phone_number}...")
        embedding = clip_service.generate_embedding_from_bytes(image_bytes)
        
        # Search similar in Pinecone
        print("Searching Pinecone for matches...")
        matches = pinecone_service.search_similar(embedding, top_k=5)
        
        # Save user to Mongo
        image_id = str(uuid.uuid4())
        print(f"Saving metadata to MongoDB for user {phone_number}...")
        await mongo_service.save_user_data(
            phone_number=phone_number,
            image_id=image_id,
            filename=file.filename
        )
        
        # Optionally, save this new image to Pinecone as well?
        # The prompt says: "the image they use would be used by the backend to map from all the images present in the vector database"
        # We will not insert user images to the DB here, only the Drive ones are inserted. Or we can insert it if needed. Let's just return matches for now.

        return UploadResponse(
            status="success",
            message="Image processed successfully.",
            matches=matches
        )
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-zip")
async def download_zip(filenames: list[str] = Body(...)):
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
            for filename in filenames:
                file_path = os.path.join("downloaded_images", filename)
                if os.path.exists(file_path):
                    zip_file.write(file_path, arcname=filename)
                
        return StreamingResponse(
            iter([zip_buffer.getvalue()]), 
            media_type="application/x-zip-compressed", 
            headers={"Content-Disposition": "attachment; filename=images.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=1008, reload=True)
