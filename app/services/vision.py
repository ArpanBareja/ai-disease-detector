import base64
import json
import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SYSTEM_PROMPT = """You are an agronomist specializing in crop and plant disease identification.
Look at the image and identify the plant, any disease or pest damage, severity, and practical next steps.
If the image is not a plant or crop, set is_plant to false and keep the remaining fields conservative.
If the plant looks healthy, set is_healthy to true and disease_name to "healthy".
Do not invent a diagnosis when the image is unclear. This is decision support, not a lab diagnosis.
"""


class CropDiseaseAnalysis(BaseModel):
    is_plant: bool = Field(description="Whether the image shows a plant or crop")
    plant_name: str = Field(description="Common name of the plant, or unknown")
    is_healthy: bool
    disease_name: str = Field(description="Disease, pest, deficiency, healthy, or unknown")
    disease_type: str = Field(
        description="fungal, bacterial, viral, pest, nutrient_deficiency, abiotic, healthy, or unknown"
    )
    confidence: float = Field(ge=0, le=1, description="Confidence from 0 to 1")
    severity: str = Field(description="none, low, moderate, or high")
    symptoms: list[str]
    likely_causes: list[str]
    treatment: list[str]
    prevention: list[str]
    notes: str = Field(description="Short explanation of the finding")


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GOOGLE_API_KEY or GEMINI_API_KEY in the environment or a .env file."
        )
    return genai.Client(api_key=api_key)


def _parse_analysis(output_text: str | None) -> dict:
    if not output_text:
        raise RuntimeError("Gemini returned an empty response for the image.")
    try:
        return CropDiseaseAnalysis.model_validate_json(output_text).model_dump()
    except Exception:
        return CropDiseaseAnalysis.model_validate(json.loads(output_text)).model_dump()


async def analyse_crop_disease(content: bytes, content_type: str) -> dict:
    client = _get_client()
    image_b64 = base64.b64encode(content).decode("utf-8")

    interaction = await client.aio.interactions.create(
        model=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
        input=[
            {"type": "text", "text": "Analyze this crop or plant image for disease."},
            {"type": "image", "data": image_b64, "mime_type": content_type},
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": CropDiseaseAnalysis.model_json_schema(),
        },
        generation_config={"temperature": 0.2},
        store=False,
    )

    if interaction.status != "completed":
        errors = getattr(interaction, "errors", None) or []
        detail = errors[0] if errors else interaction.status
        raise RuntimeError(f"Gemini interaction failed: {detail}")

    return _parse_analysis(interaction.output_text)
