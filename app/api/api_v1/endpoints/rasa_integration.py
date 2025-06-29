from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import httpx
from pydantic import BaseModel
from sqlmodel import Session
import uuid
import subprocess
import os
import time
from datetime import datetime

from app.db.database import get_db
from app.services.chatbot_interaction import ChatbotInteractionService
from app.core.config import settings
from app.db.exporters.rasa_exporter import export_nlu, export_domain, export_rules, export_stories, RASA_DIR

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

class TrainingStatus(BaseModel):
    task_id: str
    status: str
    step: int
    message: str
    error: str = None

# Dictionary to store training tasks and their status
training_tasks = {}

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

@router.post("/export-data", response_model=Dict[str, Any])
async def export_rasa_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Xuất dữ liệu từ PostgreSQL ra các file Rasa
    """
    task_id = str(uuid.uuid4())
    training_tasks[task_id] = {
        "status": "running",
        "message": "Đang xuất dữ liệu",
        "logs": [],
        "start_time": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        _export_rasa_data_task,
        task_id,
        db
    )
    
    return {"task_id": task_id}

async def _export_rasa_data_task(task_id: str, db: Session):
    """
    Task xuất dữ liệu từ PostgreSQL ra các file Rasa
    """
    try:
        # Xuất dữ liệu NLU
        training_tasks[task_id]["logs"].append("Bắt đầu xuất dữ liệu NLU...")
        export_nlu(db)
        training_tasks[task_id]["logs"].append("Đã xuất dữ liệu NLU thành công")
        
        # Xuất dữ liệu Domain
        training_tasks[task_id]["logs"].append("Bắt đầu xuất domain...")
        export_domain(db)
        training_tasks[task_id]["logs"].append("Đã xuất domain thành công")
        
        # Xuất dữ liệu Rules và Stories
        training_tasks[task_id]["logs"].append("Bắt đầu xuất rules...")
        export_rules(db)
        training_tasks[task_id]["logs"].append("Đã xuất rules thành công")
        
        training_tasks[task_id]["logs"].append("Bắt đầu xuất stories...")
        export_stories(db)
        training_tasks[task_id]["logs"].append("Đã xuất stories thành công")
        
        training_tasks[task_id]["status"] = "completed"
        training_tasks[task_id]["message"] = "Đã xuất dữ liệu thành công"
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()
    except Exception as e:
        training_tasks[task_id]["status"] = "error"
        training_tasks[task_id]["error"] = str(e)
        training_tasks[task_id]["message"] = f"Lỗi khi xuất dữ liệu: {str(e)}"
        training_tasks[task_id]["logs"].append(f"Lỗi: {str(e)}")
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()

@router.post("/train", response_model=Dict[str, Any])
async def train_rasa_model(
    background_tasks: BackgroundTasks
) -> Any:
    """
    Huấn luyện mô hình Rasa
    """
    task_id = str(uuid.uuid4())
    training_tasks[task_id] = {
        "status": "running",
        "message": "Đang huấn luyện mô hình",
        "logs": [],
        "start_time": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        _train_rasa_model_task,
        task_id
    )
    
    return {"task_id": task_id}

async def _train_rasa_model_task(task_id: str):
    """
    Task huấn luyện mô hình Rasa
    """
    try:
        # Chạy script huấn luyện mô hình
        training_tasks[task_id]["logs"].append("Bắt đầu huấn luyện mô hình Rasa...")
        
        process = subprocess.Popen(
            "/Users/linoedge/study/study-projects/chatbot/train_rasa.sh",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Đọc output theo từng dòng và cập nhật logs
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                training_tasks[task_id]["logs"].append(line.strip())
        
        # Đọc stderr nếu có
        for line in iter(process.stderr.readline, ''):
            if line.strip():
                training_tasks[task_id]["logs"].append(f"ERROR: {line.strip()}")
        
        # Đợi process hoàn thành
        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()
        
        if return_code != 0:
            training_tasks[task_id]["status"] = "error"
            training_tasks[task_id]["error"] = "Lỗi khi huấn luyện mô hình Rasa"
            training_tasks[task_id]["message"] = "Lỗi khi huấn luyện mô hình Rasa"
        else:
            training_tasks[task_id]["status"] = "completed"
            training_tasks[task_id]["message"] = "Đã huấn luyện mô hình thành công"
            training_tasks[task_id]["logs"].append("Đã huấn luyện mô hình thành công")
        
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()
    except Exception as e:
        training_tasks[task_id]["status"] = "error"
        training_tasks[task_id]["error"] = str(e)
        training_tasks[task_id]["message"] = f"Lỗi khi huấn luyện mô hình: {str(e)}"
        training_tasks[task_id]["logs"].append(f"Lỗi: {str(e)}")
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()

@router.post("/restart", response_model=Dict[str, Any])
async def restart_rasa_server(
    background_tasks: BackgroundTasks
) -> Any:
    """
    Khởi động lại Rasa server
    """
    task_id = str(uuid.uuid4())
    training_tasks[task_id] = {
        "status": "running",
        "message": "Đang khởi động lại Rasa server",
        "logs": [],
        "start_time": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        _restart_rasa_server_task,
        task_id
    )
    
    return {"task_id": task_id}

async def _restart_rasa_server_task(task_id: str):
    """
    Task khởi động lại Rasa server
    """
    try:
        # Sử dụng script để khởi động lại Rasa server
        training_tasks[task_id]["logs"].append("Bắt đầu khởi động lại Rasa server...")
        
        # Tạo file log tạm thời
        log_file = f"/tmp/rasa_restart_{task_id}.log"
        
        process = subprocess.Popen(
            f"/Users/linoedge/study/study-projects/chatbot/restart_rasa.sh > {log_file} 2>&1 &",
            shell=True
        )
        
        # Đợi một chút để Rasa khởi động
        training_tasks[task_id]["logs"].append("Đợi Rasa server khởi động...")
        time.sleep(5)
        
        # Đọc log từ file
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                log_lines = log_content.split('\n')
                for line in log_lines:
                    if line.strip():
                        training_tasks[task_id]["logs"].append(line.strip())
        except Exception as e:
            training_tasks[task_id]["logs"].append(f"Không thể đọc log: {str(e)}")
        
        # Kiểm tra xem Rasa đã khởi động thành công chưa
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.RASA_SERVER}/status", timeout=5)
                if response.status_code == 200:
                    training_tasks[task_id]["status"] = "completed"
                    training_tasks[task_id]["message"] = "Đã khởi động lại Rasa server thành công"
                    training_tasks[task_id]["logs"].append("Đã khởi động lại Rasa server thành công")
                else:
                    training_tasks[task_id]["status"] = "error"
                    training_tasks[task_id]["error"] = "Rasa server không phản hồi sau khi khởi động lại"
                    training_tasks[task_id]["message"] = "Lỗi khi khởi động lại Rasa server"
                    training_tasks[task_id]["logs"].append("Rasa server không phản hồi sau khi khởi động lại")
        except Exception:
            training_tasks[task_id]["status"] = "error"
            training_tasks[task_id]["error"] = "Không thể kết nối đến Rasa server sau khi khởi động lại"
            training_tasks[task_id]["message"] = "Lỗi khi khởi động lại Rasa server"
            training_tasks[task_id]["logs"].append("Không thể kết nối đến Rasa server sau khi khởi động lại")
        
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()
    except Exception as e:
        training_tasks[task_id]["status"] = "error"
        training_tasks[task_id]["error"] = str(e)
        training_tasks[task_id]["message"] = f"Lỗi khi khởi động lại Rasa server: {str(e)}"
        training_tasks[task_id]["logs"].append(f"Lỗi: {str(e)}")
        training_tasks[task_id]["end_time"] = datetime.now().isoformat()

@router.get("/task/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str) -> Any:
    """
    Lấy trạng thái của một task
    """
    if task_id not in training_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy task với ID {task_id}"
        )
    
    task = training_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "message": task["message"],
        "logs": task["logs"],
        "start_time": task["start_time"],
        "end_time": task.get("end_time")
    }

@router.get("/tasks/", response_model=Dict[str, Any])
async def get_all_tasks() -> Any:
    """
    Lấy danh sách tất cả các task
    """
    return training_tasks
