from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_db
from app.db.models.rasa_nlu_example import RasaNluExample
from app.db.models.rasa_intent import RasaIntent
from app.schemas.nlu_example import NluExample, NluExampleCreate, NluExampleUpdate

router = APIRouter()

@router.get("/", response_model=List[NluExample])
def read_nlu_examples(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    intent_id: int = None,
    is_active: bool = None
) -> Any:
    """
    Lấy danh sách các NLU examples.
    """
    query = select(RasaNluExample)
    if intent_id is not None:
        query = query.where(RasaNluExample.intent_id == intent_id)
    if is_active is not None:
        query = query.where(RasaNluExample.is_active == is_active)
    
    examples = db.exec(query.offset(skip).limit(limit)).all()
    return examples

@router.post("/", response_model=NluExample)
def create_nlu_example(
    *,
    db: Session = Depends(get_db),
    example_in: NluExampleCreate
) -> Any:
    """
    Tạo NLU example mới.
    """
    # Kiểm tra xem intent có tồn tại không
    intent = db.get(RasaIntent, example_in.intent_id)
    if not intent:
        raise HTTPException(
            status_code=404,
            detail=f"Intent với ID {example_in.intent_id} không tồn tại."
        )
    
    # Kiểm tra xem example đã tồn tại chưa
    existing_example = db.exec(
        select(RasaNluExample).where(
            (RasaNluExample.intent_id == example_in.intent_id) &
            (RasaNluExample.text == example_in.text)
        )
    ).first()
    
    if existing_example:
        raise HTTPException(
            status_code=400,
            detail=f"NLU example với text '{example_in.text}' đã tồn tại cho intent này."
        )
    
    example = RasaNluExample(**example_in.dict())
    db.add(example)
    db.commit()
    db.refresh(example)
    return example

@router.get("/{example_id}", response_model=NluExample)
def read_nlu_example(
    *,
    db: Session = Depends(get_db),
    example_id: int
) -> Any:
    """
    Lấy thông tin chi tiết của một NLU example.
    """
    example = db.get(RasaNluExample, example_id)
    if not example:
        raise HTTPException(
            status_code=404,
            detail=f"NLU example với ID {example_id} không tồn tại."
        )
    return example

@router.put("/{example_id}", response_model=NluExample)
def update_nlu_example(
    *,
    db: Session = Depends(get_db),
    example_id: int,
    example_in: NluExampleUpdate
) -> Any:
    """
    Cập nhật NLU example.
    """
    example = db.get(RasaNluExample, example_id)
    if not example:
        raise HTTPException(
            status_code=404,
            detail=f"NLU example với ID {example_id} không tồn tại."
        )
    
    # Cập nhật các trường nếu có trong request
    example_data = example_in.dict(exclude_unset=True)
    for field, value in example_data.items():
        setattr(example, field, value)
    
    db.add(example)
    db.commit()
    db.refresh(example)
    return example

@router.delete("/{example_id}")
def delete_nlu_example(
    *,
    db: Session = Depends(get_db),
    example_id: int
) -> Any:
    """
    Xóa NLU example.
    """
    example = db.get(RasaNluExample, example_id)
    if not example:
        raise HTTPException(
            status_code=404,
            detail=f"NLU example với ID {example_id} không tồn tại."
        )
    
    db.delete(example)
    db.commit()
    return {"message": f"NLU example với ID {example_id} đã được xóa."}
