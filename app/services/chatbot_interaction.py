from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select

from app.db.models.chatbot_interaction_log import ChatbotInteractionLog

class ChatbotInteractionService:
    """
    Service để quản lý lịch sử tương tác với chatbot
    """
    
    @staticmethod
    def log_interaction(
        db: Session,
        user_id: str,
        user_message: str,
        bot_responses: List[Dict[str, Any]],
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
        session_id: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> ChatbotInteractionLog:
        """
        Lưu lại một tương tác giữa người dùng và chatbot
        """
        # Chuyển đổi bot_responses thành chuỗi JSON
        import json
        bot_responses_str = json.dumps(bot_responses, ensure_ascii=False)
        meta_data_str = json.dumps(meta_data, ensure_ascii=False) if meta_data else None
        
        # Tạo bản ghi mới
        interaction = ChatbotInteractionLog(
            user_id=user_id,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_responses_str,
            intent=intent,
            confidence=confidence,
            meta_data=meta_data_str,
            timestamp=datetime.utcnow()
        )
        
        # Lưu vào database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        return interaction
    
    @staticmethod
    def get_user_interactions(
        db: Session,
        user_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[ChatbotInteractionLog]:
        """
        Lấy lịch sử tương tác của một người dùng
        """
        query = select(ChatbotInteractionLog).where(
            ChatbotInteractionLog.user_id == user_id
        ).order_by(ChatbotInteractionLog.timestamp.desc())
        
        interactions = db.exec(query.offset(skip).limit(limit)).all()
        return interactions
    
    @staticmethod
    def get_session_interactions(
        db: Session,
        session_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[ChatbotInteractionLog]:
        """
        Lấy lịch sử tương tác của một phiên chat
        """
        query = select(ChatbotInteractionLog).where(
            ChatbotInteractionLog.session_id == session_id
        ).order_by(ChatbotInteractionLog.timestamp.asc())
        
        interactions = db.exec(query.offset(skip).limit(limit)).all()
        return interactions
