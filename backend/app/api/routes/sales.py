# backend/app/api/routes/sales.py

from fastapi import APIRouter, UploadFile, File
from app.services.sales_reader import read_sales_file

router = APIRouter()

@router.post("/upload")
async def upload_sales(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    df = read_sales_file(path)
    return {"rows": len(df), "columns": df.columns.tolist()}
