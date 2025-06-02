from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_db
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_intent import RasaIntent
from app.schemas.response import Response, ResponseCreate, ResponseUpdate

router = APIRouter()

@router.get("/", response_model=List[Response])
def read_responses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    intent_id: int = None,
    is_active: bool = None
) -> Any:
    """
    Lấy danh sách các responses.
    """
    query = select(RasaResponse)
    if intent_id is not None:
        query = query.where(RasaResponse.intent_id == intent_id)
    if is_active is not None:
        query = query.where(RasaResponse.is_active == is_active)
    
    responses = db.exec(query.offset(skip).limit(limit)).all()
    return responses

@router.post("/", response_model=Response)
def create_response(
    *,
    db: Session = Depends(get_db),
    response_in: ResponseCreate
) -> Any:
    """
    Tạo response mới.
    """
    # Kiểm tra xem intent có tồn tại không
    intent = db.get(RasaIntent, response_in.intent_id)
    if not intent:
        raise HTTPException(
            status_code=404,
            detail=f"Intent với ID {response_in.intent_id} không tồn tại."
        )
    
    response = RasaResponse(**response_in.dict())
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

@router.get("/{response_id}", response_model=Response)
def read_response(
    *,
    db: Session = Depends(get_db),
    response_id: int
) -> Any:
    """
    Lấy thông tin chi tiết của một response.
    """
    response = db.get(RasaResponse, response_id)
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Response với ID {response_id} không tồn tại."
        )
    return response

@router.put("/{response_id}", response_model=Response)
def update_response(
    *,
    db: Session = Depends(get_db),
    response_id: int,
    response_in: ResponseUpdate
) -> Any:
    """
    Cập nhật response.
    """
    response = db.get(RasaResponse, response_id)
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Response với ID {response_id} không tồn tại."
        )
    
    # Cập nhật các trường nếu có trong request
    response_data = response_in.dict(exclude_unset=True)
    for field, value in response_data.items():
        setattr(response, field, value)
    
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

@router.delete("/{response_id}")
def delete_response(
    *,
    db: Session = Depends(get_db),
    response_id: int
) -> Any:
    """
    Xóa response.
    """
    response = db.get(RasaResponse, response_id)
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Response với ID {response_id} không tồn tại."
        )
    
    db.delete(response)
    db.commit()
    return {"message": f"Response với ID {response_id} đã được xóa."}
