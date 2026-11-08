from fastapi import FastAPI
from app.routes.analyse import router as analyse_router

app = FastAPI(
    title="Disease Detector API",
    description="API used for detecting plant based diseases"
)

@app.get("/")
async def root():
    return {
        "message": "Disease Detector API is running",
        "app": "Netra Vision App",
        "endpoints": {
            "POST /analyse": "Upload an image for disease detection",
            "POST /analyse/batch": "Upload multiple images for batch disease detection"
        }
    }

app.include_router(analyse_router)