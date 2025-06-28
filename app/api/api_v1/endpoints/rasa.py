from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
import httpx
import os
import subprocess
from datetime import datetime

from app.db.database import get_db, engine
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_nlu_example import RasaNluExample
from app.core.config import settings
from app.db.exporters.rasa_exporter import export_nlu, export_domain, export_rules, export_stories, ensure_dir_exists, RASA_DIR

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

@router.post("/train/")
async def train_rasa_model(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db)
):
    """
    Generate Rasa training files from database and train the model
    """
    # Start training in the background
    background_tasks.add_task(
        _train_rasa_model_task,
        session
    )
    
    return {"status": "Training started in the background"}

async def _train_rasa_model_task(session: Session):
    """
    Background task to generate Rasa training files and train the model
    """
    try:
        # Sử dụng các hàm từ rasa_exporter để tạo các file training
        export_nlu(session)
        export_domain(session)
        export_rules(session)
        export_stories(session)
        
        # Train the model
        subprocess.run(
            ["cd", RASA_DIR, "&&", "source", ".venv/bin/activate", "&&", "python", "-m", "rasa", "train"],
            shell=True,
            check=True
        )
        
        return {"status": "success", "message": "Model trained successfully"}
    except Exception as e:
        print(f"Error training Rasa model: {str(e)}")
        return {"status": "error", "message": str(e)}
