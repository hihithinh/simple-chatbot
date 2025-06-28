from typing import List, Optional
from sqlmodel import Session, select

from app.db.models.rasa_response import RasaResponse
from app.schemas.response import ResponseCreate, ResponseUpdate

class ResponseService:
    """
    Service để quản lý các responses trong hệ thống
    """
    
    @staticmethod
    def get_responses(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        intent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[RasaResponse]:
        """
        Lấy danh sách các responses
        """
        query = select(RasaResponse)
        if intent_id is not None:
            query = query.where(RasaResponse.intent_id == intent_id)
        if is_active is not None:
            query = query.where(RasaResponse.is_active == is_active)
        
        responses = db.exec(query.offset(skip).limit(limit)).all()
        return responses
    
    @staticmethod
    def get_response_by_id(db: Session, response_id: int) -> Optional[RasaResponse]:
        """
        Lấy thông tin chi tiết của một response theo ID
        """
        return db.get(RasaResponse, response_id)
    
    @staticmethod
    def create_response(db: Session, response_in: ResponseCreate) -> RasaResponse:
        """
        Tạo response mới
        """
        response = RasaResponse(**response_in.dict())
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def update_response(
        db: Session,
        response: RasaResponse,
        response_in: ResponseUpdate
    ) -> RasaResponse:
        """
        Cập nhật response
        """
        response_data = response_in.dict(exclude_unset=True)
        for field, value in response_data.items():
            setattr(response, field, value)
        
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def delete_response(db: Session, response: RasaResponse) -> None:
        """
        Xóa response
        """
        db.delete(response)
        db.commit()
