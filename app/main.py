from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import create_db_and_tables
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS - cho phép tất cả origins để debug
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins trong quá trình phát triển
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Tạo bảng nếu chưa tồn tại
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to Chatbot CMS API"}

# Import và đăng ký router
app.include_router(api_router, prefix=settings.API_V1_STR)
