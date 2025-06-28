from typing import List, Optional
from sqlmodel import Session, select

from app.db.models.rasa_nlu_example import RasaNluExample
from app.schemas.nlu_example import NluExampleCreate, NluExampleUpdate

class NluExampleService:
    """
    Service để quản lý các NLU examples trong hệ thống
    """
    
    @staticmethod
    def get_nlu_examples(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        intent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[RasaNluExample]:
        """
        Lấy danh sách các NLU examples
        """
        query = select(RasaNluExample)
        if intent_id is not None:
            query = query.where(RasaNluExample.intent_id == intent_id)
        if is_active is not None:
            query = query.where(RasaNluExample.is_active == is_active)
        
        examples = db.exec(query.offset(skip).limit(limit)).all()
        return examples
    
    @staticmethod
    def get_nlu_example_by_id(db: Session, example_id: int) -> Optional[RasaNluExample]:
        """
        Lấy thông tin chi tiết của một NLU example theo ID
        """
        return db.get(RasaNluExample, example_id)
    
    @staticmethod
    def get_nlu_example_by_text_and_intent(
        db: Session, 
        text: str, 
        intent_id: int
    ) -> Optional[RasaNluExample]:
        """
        Lấy thông tin chi tiết của một NLU example theo text và intent_id
        """
        return db.exec(
            select(RasaNluExample).where(
                (RasaNluExample.intent_id == intent_id) &
                (RasaNluExample.text == text)
            )
        ).first()
    
    @staticmethod
    def create_nlu_example(db: Session, example_in: NluExampleCreate) -> RasaNluExample:
        """
        Tạo NLU example mới
        """
        example = RasaNluExample(**example_in.dict())
        db.add(example)
        db.commit()
        db.refresh(example)
        return example
    
    @staticmethod
    def update_nlu_example(
        db: Session,
        example: RasaNluExample,
        example_in: NluExampleUpdate
    ) -> RasaNluExample:
        """
        Cập nhật NLU example
        """
        example_data = example_in.dict(exclude_unset=True)
        for field, value in example_data.items():
            setattr(example, field, value)
        
        db.add(example)
        db.commit()
        db.refresh(example)
        return example
    
    @staticmethod
    def delete_nlu_example(db: Session, example: RasaNluExample) -> None:
        """
        Xóa NLU example
        """
        db.delete(example)
        db.commit()
