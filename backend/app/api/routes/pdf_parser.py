from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
import os
import logging

# Try to import PyPDF2, but don't fail if it's not available
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

router = APIRouter(prefix="/pdf", tags=["PDF Parser"])
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    if not HAS_PYPDF2:
        return ""

    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return ""
    return text


@router.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Parse medicine invoice PDF using OCR.
    Extracts medicine names, quantities, prices.
    """
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and image files are supported"
        )

    os.makedirs("data/uploads", exist_ok=True)

    temp_path = f"data/uploads/{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # TODO: Implement actual PDF OCR parsing
        # For now, return mock data
        extracted_data = {
            "status": "success",
            "filename": file.filename,
            "items": [
                {
                    "medicine_name": "Paracetamol 500mg",
                    "quantity": 100,
                    "unit_price": 2.5,
                    "batch_no": "BATCH123",
                    "expiry_date": "2025-12-31"
                }
            ],
            "message": "PDF parsing is a placeholder. Implement OCR integration as needed."
        }

        logger.info(f"Parsed file: {file.filename}")
        return extracted_data

    except Exception as e:
        logger.error(f"Error parsing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}"
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
