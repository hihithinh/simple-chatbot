from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
import re
import unicodedata
import httpx
import json
import logging
import sys
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from app.db.models.data_source import DataSource
from app.db.models.crawled_content import CrawledContent
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_nlu_example import RasaNluExample
from app.db.database import get_db, engine
from app.core.config import settings
from app.utils.gpt_util import GPTUtil
import asyncio

# Configure logging with more explicit settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("qa_generator")
# Force the logger to use INFO level
logger.setLevel(logging.INFO)

# Test log to verify logging is working
logger.info("QA Generator module initialized with enhanced logging")

# Check if API key is configured
if not settings.TOGETHER_API_KEY:
    logger.error("TOGETHER_API_KEY is not configured")
    raise Exception("TOGETHER_API_KEY is not configured")

router = APIRouter()

# Initialize GPT utility
gpt_util = GPTUtil()

# Together AI API endpoint
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"

class IntentResponse(BaseModel):
    intent_id: int
    intent_name: str
    response_text: str

class QAItem(BaseModel):
    title: str
    code: str
    content: str

class NLUExampleCreate(BaseModel):
    intent_id: int
    examples: List[str]

class PreviousPointsRequest(BaseModel):
    previous_points: List[QAItem] = []

# Helper functions
def strip_accents(text):
    """Remove accents from text and convert to lowercase"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def generate_code(text: str) -> str:
    """
    Generate a slugified code from a title
    
    Args:
        text: The title to convert to a code
        
    Returns:
        A slugified version of the title suitable for use as a code
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace Vietnamese characters
    vietnamese_chars = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    
    for vietnamese, latin in vietnamese_chars.items():
        text = text.replace(vietnamese, latin)
    
    # Replace non-alphanumeric characters with underscores
    text = re.sub(r'[^a-z0-9]+', '_', text)
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    # Limit length
    if len(text) > 50:
        text = text[:50]
    
    # Ensure we have something
    if not text:
        return ""
    
    return text

async def extract_key_points(content: str, api_key: Optional[str] = None):
    """Extract key points from content using OpenAI GPT API"""
    logger.info("Extracting key points from content using GPT")
    print(f"DEBUG: Extracting key points from content length: {len(content)}")
    
    try:
        # Initialize GPT utility
        gpt_util = GPTUtil(api_key)
        
        # Extract key points
        extracted_text = await gpt_util.extract_key_points(content)
        
        logger.info(f"Successfully extracted key points with GPT, length: {len(extracted_text)}")
        print(f"DEBUG: Successfully extracted key points with GPT, length: {len(extracted_text)}")
        print(f"DEBUG: First 200 chars of extracted text: {extracted_text[:200]}...")
        
        return extracted_text
    except Exception as e:
        logger.error(f"Error extracting key points with GPT: {str(e)}")
        print(f"DEBUG ERROR: Error extracting key points with GPT: {str(e)}")
        raise Exception(f"Failed to extract key points with GPT: {str(e)}")

def create_list_dictionary(ai_response: str) -> List[dict]:
    """
    Create a list of dictionaries from AI response in CSV format with descriptive titles
    
    Args:
        ai_response: The response from AI in CSV format with descriptive titles
        
    Returns:
        List of dictionaries with title, code, and content
    """
    logger.info(f"Parsing AI response: {ai_response}")
    logger.debug(f"DEBUG: Parsing AI response: {ai_response}")
    
    result = []
    
    # Pattern to match: "Điểm thông tin #X [Title]: Content"
    pattern = r"Điểm thông tin #(\d+)\s*\[(.*?)\]:\s*(.*?)(?=\n\s*Điểm thông tin #\d+|\Z)"
    matches = re.findall(pattern, ai_response, re.DOTALL)
    
    if matches:
        logger.debug(f"Found {len(matches)} key points with 'Điểm thông tin' format")
        for idx, title, content in matches:
            # Clean up title and content
            title = title.strip()
            content = content.strip()
            
            # If title is empty, generate a default one
            if not title:
                title = f"Điểm {idx}"
            
            # Generate code from title
            code = generate_code(title)
            if not code:
                code = f"diem_{idx}"
            
            result.append({
                "title": title,
                "code": code,
                "content": content
            })
        
        logger.info(f"Created {len(result)} dictionary items from 'Điểm thông tin' format")
        return result
    
    # Fallback parsing: Try to find numbered points without the specific format
    lines = ai_response.strip().split('\n')
    current_point = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for numbered points or bullet points
        point_match = re.match(r'^(\d+)[\.:\)]|^[-*•]', line)
        
        if point_match or (current_point is None and line):
            # If we have a previous point, save it
            if current_point is not None and current_content:
                combined_content = ' '.join(current_content).strip()
                
                # Try to extract a title from the content
                title_match = re.match(r'^(.*?)[:\.]\s+(.*)', combined_content)
                if title_match:
                    title = title_match.group(1).strip()
                    content = title_match.group(2).strip()
                else:
                    # Use first few words as title if no clear separator
                    words = combined_content.split()
                    title = ' '.join(words[:min(5, len(words))]) + '...'
                    content = combined_content
                
                code = generate_code(title)
                if not code:
                    code = f"diem_{len(result) + 1}"
                
                result.append({
                    "title": title,
                    "code": code,
                    "content": content
                })
                current_content = []
            
            # Start a new point
            current_point = len(result) + 1
            current_content.append(line)
        elif current_point is not None:
            # Continue with the current point
            current_content.append(line)
    
    # Don't forget the last point
    if current_point is not None and current_content:
        combined_content = ' '.join(current_content).strip()
        
        # Try to extract a title from the content
        title_match = re.match(r'^(.*?)[:\.]\s+(.*)', combined_content)
        if title_match:
            title = title_match.group(1).strip()
            content = title_match.group(2).strip()
        else:
            # Use first few words as title if no clear separator
            words = combined_content.split()
            title = ' '.join(words[:min(5, len(words))]) + '...'
            content = combined_content
        
        code = generate_code(title)
        if not code:
            code = f"diem_{len(result) + 1}"
        
        result.append({
            "title": title,
            "code": code,
            "content": content
        })
    
    if result:
        logger.info(f"Created {len(result)} dictionary items from fallback parsing")
        return result
    
    # If all else fails, just return the whole text as one item
    logger.warning("Could not parse AI response into key points, returning as single item")
    return [{
        "title": "Thông tin tổng hợp",
        "code": "thong_tin_tong_hop",
        "content": ai_response.strip()
    }]

@router.get("/extract-key-points/{data_source_id}/", response_model=List[QAItem])
@router.post("/extract-key-points/{data_source_id}/", response_model=List[QAItem])
async def extract_key_points_from_data_source(
    data_source_id: int,
    request: PreviousPointsRequest = None,
    db: Session = Depends(get_db)
):
    """Extract key points from a data source's latest crawled content"""
    logger.info(f"Extracting key points from data source {data_source_id}")
    
    # Lấy danh sách điểm thông tin đã trích xuất trước đó (nếu có)
    previous_points = []
    if request and request.previous_points:
        previous_points = request.previous_points
        logger.info(f"Received {len(previous_points)} previously extracted points")
    
    # Get the data source
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        logger.error(f"Data source {data_source_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {data_source_id} not found"
        )
    
    logger.info(f"Found data source: {data_source.name}")
    
    # Get the latest crawled content for this data source
    crawled_content = db.query(CrawledContent)\
        .filter(CrawledContent.data_source_id == data_source_id)\
        .order_by(CrawledContent.created_at.desc())\
        .first()
    
    if not crawled_content:
        logger.error(f"No crawled content found for data source {data_source_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No crawled content found for data source with ID {data_source_id}"
        )
    
    logger.info(f"Found crawled content with ID {crawled_content.id}, length: {len(crawled_content.content)} characters")
    
    # Khởi tạo GPTUtil
    gpt_util = GPTUtil(settings.OPENAI_API_KEY)
    
    # Call GPT API to extract key points
    logger.info("Calling GPT API to extract key points")
    try:
        # Chuyển đổi previous_points thành định dạng mà GPTUtil có thể sử dụng
        formatted_previous_points = []
        if previous_points:
            formatted_previous_points = [{"title": p.title, "content": p.content} for p in previous_points]
            
        # Gọi phương thức extract_key_points với danh sách điểm đã trích xuất
        ai_response = await gpt_util.extract_key_points(
            crawled_content.content, 
            min_points=5, 
            previous_points=formatted_previous_points
        )
        
        logger.info(f"Received AI response with length: {len(ai_response)} characters")
        logger.info(f"AI response first 200 chars: {ai_response[:200]}...")
        
        # Parse the AI response into a list of dictionaries
        key_points = create_list_dictionary(ai_response)
        logger.info(f"Created {len(key_points)} key points")
        
        return key_points
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error extracting key points: {error_message}")
        
        # Xử lý các lỗi phổ biến từ OpenAI API
        if "rate_limit_exceeded" in error_message or "Rate limit exceeded" in error_message:
            if "tokens per min" in error_message:
                # Trích xuất thông tin về giới hạn token
                import re
                limit_match = re.search(r"Limit (\d+), Requested (\d+)", error_message)
                if limit_match:
                    limit = limit_match.group(1)
                    requested = limit_match.group(2)
                    error_message = f"Nội dung quá dài (yêu cầu {requested} tokens, giới hạn {limit} tokens). Vui lòng chia nhỏ nội dung hoặc thử lại sau."
                else:
                    error_message = "Đã vượt quá giới hạn tốc độ API. Hệ thống đã thử lại nhiều lần nhưng không thành công. Vui lòng thử lại sau 1-2 phút."
            else:
                error_message = "Đã vượt quá giới hạn tốc độ API. Hệ thống đã thử lại nhiều lần nhưng không thành công. Vui lòng thử lại sau 1-2 phút."
        elif "context_length_exceeded" in error_message:
            error_message = "Nội dung quá dài cho mô hình AI. Vui lòng chia nhỏ nội dung."
        elif "invalid_api_key" in error_message:
            error_message = "Lỗi xác thực API. Vui lòng kiểm tra cấu hình API key."
        elif "model_not_found" in error_message:
            error_message = "Mô hình AI không khả dụng. Vui lòng kiểm tra cấu hình hoặc thử lại sau."
        elif "Maximum retries" in error_message and "exceeded" in error_message:
            error_message = "Đã vượt quá số lần thử lại. Máy chủ OpenAI có thể đang quá tải. Vui lòng thử lại sau 1-2 phút."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

@router.post("/create-intents/{data_source_id}/", response_model=List[IntentResponse])
async def create_intents_from_key_points(
    data_source_id: int,
    key_points: List[QAItem],
    db: Session = Depends(get_db)
):
    """Create intents and responses from key points"""
    logger.info(f"Creating intents from {len(key_points)} key points for data source {data_source_id}")
    
    # Get the data source
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nguồn dữ liệu với ID {data_source_id}"
        )
    
    try:
        # Create intents and responses
        intents_responses = []
        
        for point in key_points:
            # Create intent
            intent_name = f"key_point_{point.code}"
            intent = RasaIntent(
                name=intent_name,
                description=point.title,
                data_source_id=data_source_id
            )
            db.add(intent)
            db.flush()  # Get the ID without committing
            
            # Create response
            response = RasaResponse(
                intent_id=intent.id,
                response_text=point.content,
                is_default=True
            )
            db.add(response)
            
            # Add to result list
            intents_responses.append({
                "intent_id": intent.id,
                "intent_name": intent_name,
                "response_text": point.content
            })
        
        # Commit all changes
        db.commit()
        
        logger.info(f"Created {len(intents_responses)} intents and responses")
        return intents_responses
    except Exception as e:
        db.rollback()
        error_message = str(e)
        logger.error(f"Error creating intents: {error_message}")
        
        # Xử lý các lỗi cơ sở dữ liệu phổ biến
        if "duplicate key" in error_message.lower():
            error_message = "Một số intent đã tồn tại trong cơ sở dữ liệu. Vui lòng kiểm tra lại tên intent."
        elif "foreign key" in error_message.lower():
            error_message = "Lỗi tham chiếu dữ liệu. Vui lòng kiểm tra lại nguồn dữ liệu."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

@router.post("/generate-nlu-examples/", response_model=List[str])
async def generate_nlu_examples_for_intent(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate NLU examples for an intent"""
    intent_id = data.get("intent_id")
    if not intent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu intent_id trong yêu cầu"
        )
    
    # Get the intent
    intent = db.query(RasaIntent).filter(RasaIntent.id == intent_id).first()
    if not intent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy intent với ID {intent_id}"
        )
    
    # Get the response for this intent
    response = db.query(RasaResponse).filter(RasaResponse.intent_id == intent_id).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy response cho intent với ID {intent_id}"
        )
    
    # Get the data source for this intent
    data_source = None
    if intent.data_source_id:
        data_source = db.query(DataSource).filter(DataSource.id == intent.data_source_id).first()
    
    # Use a default name if data source is not found
    data_source_name = data_source.name if data_source else "Chatbot"
    
    try:
        # Generate examples directly (not in background)
        examples = await gpt_util.generate_nlu_examples_for_intent(
            title=intent.description,
            content=response.response_text,
            notification_title=data_source_name,
            num_examples=5
        )
        
        # Save the examples to the database
        save_nlu_examples(intent_id, examples, db)
        
        return examples
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating NLU examples: {error_message}")
        
        if "rate_limit_exceeded" in error_message:
            error_message = "Đã vượt quá giới hạn tốc độ API. Vui lòng thử lại sau ít phút."
        elif "context_length_exceeded" in error_message:
            error_message = "Nội dung quá dài cho mô hình AI. Vui lòng chia nhỏ nội dung."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

def save_nlu_examples(intent_id: int, examples: List[str], db: Session):
    """Save NLU examples to the database"""
    for example in examples:
        nlu_example = RasaNluExample(
            intent_id=intent_id,
            text=example
        )
        db.add(nlu_example)
    
    db.commit()

@router.post("/bulk-generate-nlu-examples/")
def bulk_generate_nlu_examples(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate NLU examples for multiple intents"""
    intent_ids = data.get("intent_ids")
    if not intent_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Intent IDs are required"
        )
    
    # Get the intents
    intents = []
    for intent_id in intent_ids:
        intent = db.get(RasaIntent, intent_id)
        if intent:
            intents.append(intent)
    
    if not intents:
        raise HTTPException(status_code=404, detail="No valid intents found")
    
    # Start the background task
    background_tasks.add_task(
        generate_nlu_examples_for_multiple_intents,
        intents=intents,
        db=db
    )
    
    return {"message": f"Started generating NLU examples for {len(intents)} intents"}

def generate_nlu_examples_for_multiple_intents(intents, db):
    """Generate NLU examples for multiple intents"""
    try:
        # Chuẩn bị dữ liệu cho bulk generation
        intents_data = []
        for intent in intents:
            # Lấy response cho intent này
            response = db.exec(
                select(RasaResponse).where(RasaResponse.intent_id == intent.id).limit(1)
            ).first()
            
            if not response:
                continue
                
            intents_data.append({
                "id": intent.id,
                "name": intent.name,
                "description": intent.description,
                "response_text": response.response_text
            })
        
        if not intents_data:
            logger.warning("No valid intents with responses found for bulk generation")
            return
            
        # Sử dụng GPT để tạo câu hỏi cho tất cả intent cùng một lúc
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            gpt_util.generate_nlu_examples_bulk(intents_data)
        )
        
        # Lưu các câu hỏi vào database
        for intent_id, examples in results.items():
            for example in examples:
                nlu_example = RasaNluExample(
                    intent_id=intent_id,
                    text=example
                )
                db.add(nlu_example)
            
        db.commit()
        logger.info(f"Successfully generated and saved NLU examples for {len(results)} intents")
        
    except Exception as e:
        logger.error(f"Error in bulk NLU example generation: {str(e)}")
        # Không raise exception vì đây là background task

@router.get("/intents/{data_source_id}/", response_model=List[IntentResponse])
def get_intents_for_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Get all intents and responses for a data source"""
    # Get the data source
    data_source = db.get(DataSource, data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Get all intents for this data source
    intents = db.exec(
        select(RasaIntent).where(RasaIntent.data_source_id == data_source_id)
    ).all()
    
    result = []
    
    for intent in intents:
        # Get the response for this intent
        response = db.exec(
            select(RasaResponse).where(RasaResponse.intent_id == intent.id).limit(1)
        ).first()
        
        if response:
            result.append({
                "intent_id": intent.id,
                "intent_name": intent.name,
                "response_text": response.response_text
            })
    
    return result

def generate_nlu_examples(title, content, notification_title):
    """Generate NLU examples for an intent"""
    try:
        # Create a new event loop for non-async contexts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        examples = loop.run_until_complete(
            gpt_util.generate_nlu_examples_for_intent(
                title=title,
                content=content,
                notification_title=notification_title,
                num_examples=5
            )
        )
        loop.close()
        return examples
    except Exception as e:
        # Log chi tiết lỗi
        error_detail = f"Error generating NLU examples: {str(e)}"
        logger.error(error_detail)
        
        if "rate_limit_exceeded" in str(e).lower():
            error_detail = "Đã vượt quá giới hạn tốc độ API. Vui lòng thử lại sau ít phút."
        elif "context_length_exceeded" in str(e).lower():
            error_detail = "Nội dung quá dài cho mô hình AI. Vui lòng chia nhỏ nội dung."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
