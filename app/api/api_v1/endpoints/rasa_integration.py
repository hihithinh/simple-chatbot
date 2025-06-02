from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends
import httpx
from pydantic import BaseModel
from sqlmodel import Session
import uuid

from app.db.database import get_db
from app.services.chatbot_interaction import ChatbotInteractionService
from app.core.config import settings

router = APIRouter()

class RasaMessage(BaseModel):
    sender: str
    message: str
    session_id: str = None

class RasaResponse(BaseModel):
    recipient_id: str
    text: str
    buttons: list = []
    image: str = None
    attachment: str = None
    elements: list = []
    custom: Dict[str, Any] = None

@router.post("/webhook", response_model=Dict[str, Any])
async def rasa_webhook(message: RasaMessage) -> Any:
    """
    Webhook để gửi tin nhắn đến Rasa và nhận phản hồi.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json={"sender": message.sender, "message": message.message}
            )
            response.raise_for_status()
            return {"responses": response.json()}
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi giao tiếp với Rasa server: {str(e)}"
        )

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_rasa(
    message: RasaMessage,
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint để chat với Rasa và lưu lại lịch sử trò chuyện.
    """
    try:
        # Tạo session_id nếu chưa có
        session_id = message.session_id or str(uuid.uuid4())
        
        # Gửi tin nhắn đến Rasa
        async with httpx.AsyncClient() as client:
            # Gửi tin nhắn đến Rasa
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json={"sender": message.sender, "message": message.message}
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
                    json={"text": message.message}
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
                user_id=message.sender,
                user_message=message.message,
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
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi giao tiếp với Rasa server: {str(e)}"
        )

@router.get("/health")
async def check_rasa_health() -> Dict[str, Any]:
    """
    Kiểm tra trạng thái của Rasa server.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.RASA_SERVER}/status")
            response.raise_for_status()
            return {"status": "online", "details": response.json()}
    except httpx.HTTPError:
        return {"status": "offline", "details": "Không thể kết nối đến Rasa server"}

@router.get("/interactions/{user_id}", response_model=Dict[str, Any])
async def get_user_interactions(
    user_id: str,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy lịch sử tương tác của một người dùng
    """
    interactions = ChatbotInteractionService.get_user_interactions(
        db=db,
        user_id=user_id,
        limit=limit,
        skip=skip
    )
    
    return {
        "user_id": user_id,
        "total": len(interactions),
        "interactions": interactions
    }

@router.get("/interactions/session/{session_id}", response_model=Dict[str, Any])
async def get_session_interactions(
    session_id: str,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy lịch sử tương tác của một phiên chat
    """
    interactions = ChatbotInteractionService.get_session_interactions(
        db=db,
        session_id=session_id,
        limit=limit,
        skip=skip
    )
    
    return {
        "session_id": session_id,
        "total": len(interactions),
        "interactions": interactions
    }
