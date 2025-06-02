from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_db
from app.db.models.rasa_intent import RasaIntent
from app.schemas.intent import Intent, IntentCreate, IntentUpdate

router = APIRouter()

@router.get("/", response_model=List[Intent])
def read_intents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None
) -> Any:
    """
    Lấy danh sách các intent.
    """
    query = select(RasaIntent)
    if is_active is not None:
        query = query.where(RasaIntent.is_active == is_active)
    
    intents = db.exec(query.offset(skip).limit(limit)).all()
    return intents

@router.post("/", response_model=Intent)
def create_intent(
    *,
    db: Session = Depends(get_db),
    intent_in: IntentCreate
) -> Any:
    """
    Tạo intent mới.
    """
    # Kiểm tra xem intent đã tồn tại chưa
    existing_intent = db.exec(
        select(RasaIntent).where(RasaIntent.name == intent_in.name)
    ).first()
    
    if existing_intent:
        raise HTTPException(
            status_code=400,
            detail=f"Intent với tên '{intent_in.name}' đã tồn tại."
        )
    
    intent = RasaIntent(**intent_in.dict())
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent

@router.get("/{intent_id}", response_model=Intent)
def read_intent(
    *,
    db: Session = Depends(get_db),
    intent_id: int
) -> Any:
    """
    Lấy thông tin chi tiết của một intent.
    """
    intent = db.get(RasaIntent, intent_id)
    if not intent:
        raise HTTPException(
            status_code=404,
            detail=f"Intent với ID {intent_id} không tồn tại."
        )
    return intent

@router.put("/{intent_id}", response_model=Intent)
def update_intent(
    *,
    db: Session = Depends(get_db),
    intent_id: int,
    intent_in: IntentUpdate
) -> Any:
    """
    Cập nhật intent.
    """
    intent = db.get(RasaIntent, intent_id)
    if not intent:
        raise HTTPException(
            status_code=404,
            detail=f"Intent với ID {intent_id} không tồn tại."
        )
    
    # Cập nhật các trường nếu có trong request
    intent_data = intent_in.dict(exclude_unset=True)
    for field, value in intent_data.items():
        setattr(intent, field, value)
    
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent

@router.delete("/{intent_id}")
def delete_intent(
    *,
    db: Session = Depends(get_db),
    intent_id: int
) -> Any:
    """
    Xóa intent.
    """
    intent = db.get(RasaIntent, intent_id)
    if not intent:
        raise HTTPException(
            status_code=404,
            detail=f"Intent với ID {intent_id} không tồn tại."
        )
    
    db.delete(intent)
    db.commit()
    return {"message": f"Intent với ID {intent_id} đã được xóa."}
