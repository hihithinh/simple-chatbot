from typing import Dict, Any, Optional, List
import httpx
import uuid
from sqlmodel import Session

from app.core.config import settings
from app.services.chatbot_interaction import ChatbotInteractionService

class RasaIntegrationService:
    """
    Service để quản lý tương tác với Rasa server
    """
    
    @staticmethod
    async def send_message_to_rasa(sender: str, message: str) -> List[Dict[str, Any]]:
        """
        Gửi tin nhắn đến Rasa server và nhận phản hồi
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json={"sender": sender, "message": message}
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def parse_message(message: str) -> Dict[str, Any]:
        """
        Gửi tin nhắn đến Rasa để phân tích intent và entities
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RASA_SERVER}/model/parse",
                json={"text": message}
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def check_health() -> Dict[str, Any]:
        """
        Kiểm tra trạng thái của Rasa server
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.RASA_SERVER}/status")
                response.raise_for_status()
                return {"status": "online", "details": response.json()}
        except httpx.HTTPError:
            return {"status": "offline", "details": "Không thể kết nối đến Rasa server"}
    
    @staticmethod
    async def chat_with_rasa(
        db: Session,
        sender: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat với Rasa và lưu lịch sử trò chuyện
        """
        # Tạo session_id nếu chưa có
        session_id = session_id or str(uuid.uuid4())
        
        # Gửi tin nhắn đến Rasa
        async with httpx.AsyncClient() as client:
            # Gửi tin nhắn đến Rasa
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json={"sender": sender, "message": message}
            )
            response.raise_for_status()
            rasa_responses = response.json()
            
            # Lấy thông tin intent và confidence nếu có
            intent_info = None
            confidence = None
            
            try:
                # Gọi API parse để lấy intent và confidence
                parse_response = await client.post(
                    f"{settings.RASA_SERVER}/model/parse",
                    json={"text": message}
                )
                parse_response.raise_for_status()
                parse_data = parse_response.json()
                
                if "intent" in parse_data and parse_data["intent"]:
                    intent_info = parse_data["intent"].get("name")
                    confidence = parse_data["intent"].get("confidence")
            except Exception:
                # Nếu không lấy được intent, bỏ qua
                pass
            
            # Lưu lịch sử trò chuyện vào database
            ChatbotInteractionService.log_interaction(
                db=db,
                user_id=sender,
                user_message=message,
                bot_responses=rasa_responses,
                intent=intent_info,
                confidence=confidence,
                session_id=session_id,
                meta_data={"source": "api"}
            )
            
            return {
                "session_id": session_id,
                "responses": rasa_responses,
                "intent": intent_info,
                "confidence": confidence
            }
