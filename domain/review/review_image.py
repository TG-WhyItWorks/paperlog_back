from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os, uuid, shutil

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[-1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return JSONResponse({
        "image_url": f"/static/uploads/{unique_filename}"
    })