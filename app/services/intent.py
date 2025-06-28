from typing import List, Optional
from sqlmodel import Session, select

from app.db.models.rasa_intent import RasaIntent
from app.schemas.intent import IntentCreate, IntentUpdate

class IntentService:
    """
    Service để quản lý các intent trong hệ thống
    """
    
    @staticmethod
    def get_intents(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[RasaIntent]:
        """
        Lấy danh sách các intent
        """
        query = select(RasaIntent)
        if is_active is not None:
            query = query.where(RasaIntent.is_active == is_active)
        
        intents = db.exec(query.offset(skip).limit(limit)).all()
        return intents
    
    @staticmethod
    def get_intent_by_id(db: Session, intent_id: int) -> Optional[RasaIntent]:
        """
        Lấy thông tin chi tiết của một intent theo ID
        """
        return db.get(RasaIntent, intent_id)
    
    @staticmethod
    def get_intent_by_name(db: Session, name: str) -> Optional[RasaIntent]:
        """
        Lấy thông tin chi tiết của một intent theo tên
        """
        return db.exec(select(RasaIntent).where(RasaIntent.name == name)).first()
    
    @staticmethod
    def create_intent(db: Session, intent_in: IntentCreate) -> RasaIntent:
        """
        Tạo intent mới
        """
        intent = RasaIntent(**intent_in.dict())
        db.add(intent)
        db.commit()
        db.refresh(intent)
        return intent
    
    @staticmethod
    def update_intent(
        db: Session,
        intent: RasaIntent,
        intent_in: IntentUpdate
    ) -> RasaIntent:
        """
        Cập nhật intent
        """
        intent_data = intent_in.dict(exclude_unset=True)
        for field, value in intent_data.items():
            setattr(intent, field, value)
        
        db.add(intent)
        db.commit()
        db.refresh(intent)
        return intent
    
    @staticmethod
    def delete_intent(db: Session, intent: RasaIntent) -> None:
        """
        Xóa intent
        """
        db.delete(intent)
        db.commit()
