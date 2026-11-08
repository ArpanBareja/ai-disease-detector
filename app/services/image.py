from typing_extensions import Dict
from PIL  import Image
import io, os

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "ico", "webp"}
def validate_image(content: bytes, content_type: str) -> dict:

    if not content_type.startswith("image/"):
        return {"isValid": False, "message": "Invalid image content type"}

    if content_type.split("/")[1] not in ALLOWED_EXTENSIONS:
       return {"isValid": False, "message": "Invalid image extension"}

    if len(content) > 10 * 1024 * 1024:
       return {"isValid": False, "message": "Image too large"}

    image = Image.open(io.BytesIO(content))
    width, height = image.size

    return {
        "isValid": True,
        "message": "Image validated successfully",
        "width": width,
        "height": height,
        "content_type": content_type,
        "file_size": len(content)
    }


def save_image(content: bytes, filename: str, path: str) -> str:    
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path
