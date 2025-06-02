from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

# Tạo engine kết nối đến PostgreSQL
engine = create_engine(settings.DATABASE_URI, echo=True)

# Dependency
def get_db():
    """
    Hàm này trả về một session để tương tác với database.
    Được sử dụng như một dependency trong FastAPI.
    """
    with Session(engine) as session:
        yield session

# Tạo tất cả bảng
def create_db_and_tables():
    """
    Tạo tất cả các bảng trong database nếu chưa tồn tại.
    """
    SQLModel.metadata.create_all(engine)
