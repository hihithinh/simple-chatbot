from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
import httpx
import os
from datetime import datetime

from app.db.database import get_db, engine
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_nlu_example import RasaNluExample
from app.core.config import settings

router = APIRouter()

@router.get("/health/")
async def check_rasa_health():
    """
    Check if Rasa server is running and healthy
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.RASA_SERVER}/status")
            return {"status": "ok" if response.status_code == 200 else "error"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/webhook/")
async def rasa_webhook(request_data: Dict):
    """
    Forward webhook request to Rasa server
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json=request_data
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Rasa: {str(e)}")

@router.post("/chat/")
async def chat_with_rasa(
    request_data: Dict,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db)
):
    """
    Send a message to Rasa and store the interaction
    """
    try:
        # Forward the request to Rasa
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RASA_SERVER}/webhooks/rest/webhook",
                json={
                    "sender": request_data.get("sender", "user"),
                    "message": request_data.get("message")
                }
            )
            
            rasa_response = response.json()
            
            # Store the interaction in the database
            # This would be implemented in a real application
            
            return {
                "responses": rasa_response,
                "session_id": request_data.get("session_id")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Rasa: {str(e)}")
