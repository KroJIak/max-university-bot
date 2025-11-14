"""API эндпоинт для загрузки CSV файлов"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from core.database import get_db
from services.csv_parser import CSVParser
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UploadResponse(BaseModel):
    """Ответ на загрузку CSV"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    imported: Optional[dict] = None
    rows_count: Optional[int] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    university_id: int = Form(..., description="ID университета"),
    file: UploadFile = File(..., description="CSV файл с данными"),
    db: Session = Depends(get_db)
):
    """Загрузить CSV файл с данными для университета
    
    Принимает CSV файл и university_id, парсит данные и сохраняет в БД.
    """
    # Проверяем, что файл - CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть в формате CSV"
        )
    
    try:
        # Читаем содержимое файла
        csv_content = await file.read()
        
        # Парсим и импортируем данные
        parser = CSVParser(db, university_id)
        result = parser.parse_and_import(csv_content)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Ошибка при парсинге CSV")
            )
        
        return UploadResponse(
            success=True,
            message=result.get("message"),
            imported=result.get("imported"),
            rows_count=result.get("rows_count")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )

