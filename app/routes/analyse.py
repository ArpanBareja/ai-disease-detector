import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image import validate_image, save_image
from app.services.vision import analyse_crop_disease

router = APIRouter(
    prefix="/analyse",
    tags=["Analyse"]
)


async def process_single_image(file: UploadFile):
    content = await file.read()
    content_type = file.content_type or ""
    validation_result = validate_image(content, content_type)
    if not validation_result["isValid"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])

    extension = content_type.split("/")[1]
    unique_name = f"{uuid.uuid4()}.{extension}"
    save_image(content, unique_name, "images")
    analysis_result = await analyse_crop_disease(content, content_type)
    return {
        "analysis_result": analysis_result,
        "file_size": len(content),
    }


@router.post("/")
async def analyse(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    result = await process_single_image(file)

    return {
        "filename": file.filename,
        "analysis_result": result["analysis_result"],
        "content_type": file.content_type,
        "file_size": result["file_size"],
        "message": "Image processed and analysed successfully"
    }


@router.post("/batch")
async def analyse_batch(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        result = await process_single_image(file)
        results.append({
            "filename": file.filename,
            "analysis_result": result["analysis_result"],
            "content_type": file.content_type,
            "file_size": result["file_size"],
        })

    return {
        "results": results,
        "message": "Batch analysis complete",
    }