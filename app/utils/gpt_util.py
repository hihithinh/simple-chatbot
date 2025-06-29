import os
import json
import logging
import httpx
import re
import tiktoken
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import time
import random

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GPTMessage(BaseModel):
    role: str
    content: str

class GPTUtil:
    """Utility class for interacting with OpenAI GPT API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is not set. Set it in .env as OPENAI_API_KEY")
        
        self.base_url = "https://api.openai.com/v1"
        self.use_gpt4 = os.getenv("USE_GPT4", "false").lower() == "true"
        self.default_model = "gpt-4o" if self.use_gpt4 else "gpt-3.5-turbo"
        
        # Maximum tokens to process in a single API call
        self.max_chunk_tokens = 10000
        self.max_retries = 5  # Maximum number of retries for rate limit errors
        self.base_retry_delay = 2  # Base delay in seconds for exponential backoff
    
    def num_tokens_from_string(self, string: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Calculate the number of tokens in a text string for a specific model
        
        Args:
            string: The text string to count tokens for
            model: The model name to use for token counting
            
        Returns:
            Number of tokens in the string
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(string))
        except Exception:
            # Fallback to approximate token count if tiktoken fails
            return len(string) // 4  # Rough approximation: ~4 chars per token
    
    def num_tokens_from_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Calculate the total number of tokens in a list of messages
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            Total number of tokens in the messages
        """
        total_tokens = 0
        for message in messages:
            total_tokens += self.num_tokens_from_string(message["content"])
        return total_tokens
    
    def split_text_into_chunks(self, text: str, max_tokens: int = None) -> List[str]:
        """
        Split a long text into smaller chunks based on token count
        
        Args:
            text: The text to split
            max_tokens: Maximum tokens per chunk (defaults to self.max_chunk_tokens)
            
        Returns:
            List of text chunks
        """
        if max_tokens is None:
            max_tokens = self.max_chunk_tokens
            
        # If text is short enough, return as is
        if self.num_tokens_from_string(text) <= max_tokens:
            return [text]
        
        # Split text into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self.num_tokens_from_string(paragraph)
            
            # If a single paragraph is too large, split it into sentences
            if paragraph_tokens > max_tokens:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    sentence_tokens = self.num_tokens_from_string(sentence)
                    
                    # If adding this sentence would exceed the limit, start a new chunk
                    if current_tokens + sentence_tokens > max_tokens and current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = sentence
                        current_tokens = sentence_tokens
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                        current_tokens += sentence_tokens
            else:
                # If adding this paragraph would exceed the limit, start a new chunk
                if current_tokens + paragraph_tokens > max_tokens and current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                    current_tokens = paragraph_tokens
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                    current_tokens += paragraph_tokens
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> str:
        """
        Send a request to the OpenAI Chat Completions API with retry mechanism
        
        Args:
            messages: List of message objects with role and content
            model: The model to use (defaults to gpt-3.5-turbo)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum number of tokens to generate
            top_p: Controls diversity via nucleus sampling
            frequency_penalty: Penalizes repeated tokens
            presence_penalty: Penalizes repeated topics
            
        Returns:
            The generated text response
        """
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        logger.info(f"Sending request to OpenAI API with model: {model}")
        logger.debug(f"Request payload: {json.dumps(payload)[:500]}...")
        
        retries = 0
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        content = response_data["choices"][0]["message"]["content"]
                        logger.info(f"Successfully received response from OpenAI API, length: {len(content)}")
                        return content
                    elif response.status_code == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_msg = f"Error from OpenAI API: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                        
            except Exception as e:
                if retries >= self.max_retries:
                    logger.error(f"Maximum retries ({self.max_retries}) exceeded for error: {str(e)}")
                    raise
                
                # Exponential backoff with jitter
                delay = (self.base_retry_delay ** (retries + 1)) + random.uniform(0, 1)
                logger.warning(f"Error: {str(e)}. Retrying in {delay:.2f} seconds (attempt {retries + 1}/{self.max_retries})")
                await asyncio.sleep(delay)
                retries += 1
    
    async def extract_key_points_from_chunk(self, content_chunk: str, min_points: int = 5, previous_points: List[Dict[str, str]] = None) -> str:
        """
        Extract key points from a single content chunk using GPT
        
        Args:
            content_chunk: A chunk of text content to extract key points from
            min_points: Minimum number of key points to extract from this chunk
            previous_points: List of previously extracted points to avoid duplication
            
        Returns:
            Formatted string with extracted key points in CSV format with descriptive titles
        """
        if previous_points is None:
            previous_points = []
            
        system_message = {
            "role": "system", 
            "content": "Bạn là một trợ lý AI chuyên phân tích và trích xuất thông tin chính từ văn bản. "
                      "Nhiệm vụ của bạn là đọc nội dung và trích xuất các điểm thông tin quan trọng nhất, "
                      "đảm bảo mỗi điểm đều có tiêu đề tóm tắt ngắn gọn và nội dung chi tiết đầy đủ."
        }
        
        previous_points_text = ""
        if previous_points:
            previous_points_text = "Danh sách điểm thông tin đã trích xuất trước đó (KHÔNG TRÍCH XUẤT LẠI CÁC ĐIỂM NÀY):\n"
            for i, point in enumerate(previous_points):
                previous_points_text += f"{i+1}. [{point['title']}]: {point['content']}\n"
        
        user_message = {
            "role": "user",
            "content": f"""Phân tích nội dung sau và trích xuất các điểm thông tin chính.

Nội dung:
{content_chunk}

Yêu cầu:
1. Trích xuất tất cả thông tin có thể, tối thiểu {min_points} điểm thông tin chính từ nội dung.
2. Định dạng kết quả theo cấu trúc sau:
   Điểm thông tin #1 [Tiêu đề tóm tắt ngắn gọn]: Nội dung chi tiết của điểm thông tin 1.
   Điểm thông tin #2 [Tiêu đề tóm tắt ngắn gọn]: Nội dung chi tiết của điểm thông tin 2.
   ...
   
3. Tiêu đề phải tóm tắt được nội dung chính của điểm thông tin, như tiêu đề của một bài báo.
4. Đảm bảo mỗi điểm thông tin có đủ nội dung chi tiết để người dùng hiểu được.
5. Không bao gồm thông tin không liên quan hoặc không quan trọng.
6. Mỗi điểm thông tin phải bắt đầu bằng "Điểm thông tin #" theo sau là số thứ tự, tiêu đề trong ngoặc vuông và dấu hai chấm.
7. Bỏ qua phần bài viết liên quan

{previous_points_text}

Vui lòng trích xuất các điểm thông tin chính ngay bây giờ:"""
        }
        
        messages = [system_message, user_message]
        
        # Kiểm tra tổng kích thước token của messages
        total_tokens = self.num_tokens_from_messages(messages)
        logger.info(f"Total tokens for request: {total_tokens}")
        
        # Đảm bảo tổng kích thước token không vượt quá giới hạn
        max_allowed_tokens = self.max_chunk_tokens - 2000  # Để lại không gian cho phản hồi
        
        if total_tokens > max_allowed_tokens:
            logger.warning(f"Request too large ({total_tokens} tokens), reducing content")
            
            # Tính toán số token cần cắt bỏ
            tokens_to_reduce = total_tokens - max_allowed_tokens + 500  # Thêm 500 token đệm
            
            # Ước tính số ký tự cần cắt bỏ (trung bình 4 ký tự/token)
            chars_to_reduce = tokens_to_reduce * 4
            
            # Cắt bỏ nội dung
            reduced_content = content_chunk[:-chars_to_reduce] if len(content_chunk) > chars_to_reduce else content_chunk[:int(len(content_chunk)/2)]
            
            # Cập nhật nội dung
            user_message["content"] = user_message["content"].replace(content_chunk, reduced_content)
            messages = [system_message, user_message]
            
            # Kiểm tra lại kích thước token
            new_total_tokens = self.num_tokens_from_messages(messages)
            logger.info(f"Reduced request to {new_total_tokens} tokens")
        
        try:
            return await self.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused responses
                max_tokens=2000,   # Allow more tokens for detailed responses
                model=self.default_model
            )
        except Exception as e:
            logger.error(f"Error extracting key points from chunk: {str(e)}")
            raise
    
    async def extract_key_points(self, content: str, min_points: int = 5, previous_points: List[Dict[str, str]] = None) -> str:
        """
        Extract key points from content, chunking if necessary
        
        Args:
            content: The content to extract key points from
            min_points: Minimum number of key points to extract
            previous_points: List of previously extracted points to avoid duplication
            
        Returns:
            Formatted string with extracted key points
        """
        # Initialize previous_points if None
        if previous_points is None:
            previous_points = []
            
        # Estimate token count
        token_count = self.num_tokens_from_string(content)
        logger.info(f"Content length: {len(content)} characters, approximately {token_count} tokens")
        
        # Giảm kích thước max_chunk_tokens để đảm bảo có đủ không gian cho prompt và các phần khác
        # Giảm 20% để đảm bảo an toàn
        safe_max_chunk_tokens = int(self.max_chunk_tokens * 0.8)
        logger.info(f"Using safe max chunk size of {safe_max_chunk_tokens} tokens")
        
        # If content is short enough, process it directly
        if token_count < safe_max_chunk_tokens:
            logger.info("Content is short enough to process in one chunk")
            return await self.extract_key_points_from_chunk(content, min_points, previous_points)
        
        # Otherwise, split into chunks and process each
        logger.info(f"Content is too long ({token_count} tokens), splitting into chunks")
        chunks = self.split_text_into_chunks(content, max_tokens=safe_max_chunk_tokens)
        logger.info(f"Split content into {len(chunks)} chunks")
        
        # Process each chunk
        results = []
        extracted_points = previous_points.copy() if previous_points else []  # Start with provided previous points
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            chunk_token_count = self.num_tokens_from_string(chunk)
            logger.info(f"Chunk {i+1} size: {len(chunk)} characters, approximately {chunk_token_count} tokens")
            
            # Kiểm tra lại kích thước chunk
            if chunk_token_count > safe_max_chunk_tokens:
                logger.warning(f"Chunk {i+1} is still too large ({chunk_token_count} tokens), splitting further")
                sub_chunks = self.split_text_into_chunks(chunk, max_tokens=safe_max_chunk_tokens)
                logger.info(f"Split chunk {i+1} into {len(sub_chunks)} sub-chunks")
                
                # Xử lý từng sub-chunk
                for j, sub_chunk in enumerate(sub_chunks):
                    logger.info(f"Processing sub-chunk {j+1}/{len(sub_chunks)} of chunk {i+1}")
                    sub_chunk_result = await self.extract_key_points_from_chunk(
                        sub_chunk,
                        min_points=min(min_points, 2),  # Ít điểm hơn cho mỗi sub-chunk
                        previous_points=extracted_points
                    )
                    
                    # Extract the points from this sub-chunk's result to pass to the next sub-chunk
                    new_points = self.extract_points_from_result(sub_chunk_result)
                    extracted_points.extend(new_points)
                    
                    results.append(sub_chunk_result)
            else:
                # Pass the already extracted points to avoid duplication
                chunk_result = await self.extract_key_points_from_chunk(
                    chunk, 
                    min_points=min(min_points, 3),  # Fewer points per chunk
                    previous_points=extracted_points
                )
                
                # Extract the points from this chunk's result to pass to the next chunk
                new_points = self.extract_points_from_result(chunk_result)
                extracted_points.extend(new_points)
                
                results.append(chunk_result)
        
        # Combine results
        combined_result = "\n\n".join(results)
        
        # If we have multiple chunks, summarize to avoid redundancy
        if len(chunks) > 1:
            logger.info("Summarizing combined results to remove redundancy")
            return await self.summarize_key_points(combined_result, min_points)
        
        return combined_result
    
    def extract_points_from_result(self, result: str) -> list:
        """
        Extract points from a result string
        
        Args:
            result: The result string containing key points
            
        Returns:
            List of extracted points (title and content)
        """
        points = []
        pattern = r"Điểm thông tin #\d+\s*\[(.*?)\]:\s*(.*?)(?=\n\s*Điểm thông tin #\d+|\Z)"
        matches = re.findall(pattern, result, re.DOTALL)
        
        for title, content in matches:
            points.append({
                "title": title.strip(),
                "content": content.strip()
            })
        
        return points
    
    async def summarize_key_points(self, content: str, min_points: int = 5) -> str:
        """
        Summarize key points from content
        
        Args:
            content: The content to summarize
            min_points: Minimum number of key points to summarize
            
        Returns:
            Formatted string with summarized key points
        """
        system_message = {
            "role": "system", 
            "content": "Bạn là một trợ lý AI chuyên tổng hợp và tóm tắt thông tin. "
                      "Nhiệm vụ của bạn là tổng hợp các điểm thông tin đã được trích xuất, "
                      "loại bỏ các điểm trùng lặp và sắp xếp chúng theo thứ tự quan trọng."
        }
        
        user_message = {
            "role": "user",
            "content": f"""Tổng hợp các điểm thông tin chính từ nội dung sau:

{content}

Yêu cầu:
1. Tổng hợp tất cả thông tin có thể, tối thiểu {min_points} điểm thông tin chính.
2. Định dạng kết quả theo cấu trúc sau:
   Điểm thông tin #1 [Tiêu đề tóm tắt ngắn gọn]: Nội dung chi tiết của điểm thông tin 1.
   Điểm thông tin #2 [Tiêu đề tóm tắt ngắn gọn]: Nội dung chi tiết của điểm thông tin 2.
   ...
   
3. Tiêu đề phải tóm tắt được nội dung chính của điểm thông tin, như tiêu đề của một bài báo.
4. Đảm bảo mỗi điểm thông tin có đủ nội dung chi tiết để người dùng hiểu được.
5. Không bao gồm thông tin không liên quan hoặc không quan trọng.
6. Mỗi điểm thông tin phải bắt đầu bằng "Điểm thông tin #" theo sau là số thứ tự, tiêu đề trong ngoặc vuông và dấu hai chấm.

Vui lòng tổng hợp các điểm thông tin chính ngay bây giờ:"""
        }
        
        messages = [system_message, user_message]
        
        try:
            return await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                model=self.default_model
            )
        except Exception as e:
            logger.error(f"Error summarizing key points: {str(e)}")
            raise

    async def generate_nlu_examples_for_intent(self, title: str, content: str, notification_title: str = "", num_examples: int = 5) -> List[str]:
        """
        Generate NLU examples for an intent using GPT
        
        Args:
            title: The title or name of the intent
            content: The content or response text for the intent
            notification_title: Optional notification title for context
            num_examples: Number of examples to generate (minimum)
            
        Returns:
            List of generated NLU examples
        """
        system_message = {
            "role": "system", 
            "content": "Bạn là một trợ lý AI chuyên tạo câu hỏi mẫu cho chatbot. "
                      "Nhiệm vụ của bạn là tạo ra các câu hỏi đa dạng mà người dùng có thể hỏi "
                      "dựa trên tiêu đề và nội dung được cung cấp."
        }
        
        user_message = {
            "role": "user",
            "content": f"""Hãy giúp tôi tạo ra ít nhất {num_examples} câu hỏi mà người dùng có thể hỏi được suy luận từ tiêu đề "{title}" và nội dung "{content}"{' trong thông báo có tiêu đề "' + notification_title + '"' if notification_title else ''}.
            
Yêu cầu:
1. Câu hỏi phải liên quan trực tiếp đến nội dung.
2. Câu hỏi phải đa dạng về cách hỏi.
3. Câu hỏi phải tự nhiên như người dùng thực sự hỏi.
4. Mỗi câu hỏi phải bắt đầu bằng "Câu Hỏi Là: " và kết thúc bằng dấu chấm hỏi.
5. Câu hỏi phải bằng tiếng Việt.

Ví dụ:
Câu Hỏi Là: Làm thế nào để tôi đăng ký tài khoản?
"""
        }
        
        messages = [system_message, user_message]
        
        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                model=self.default_model
            )
            
            # Extract questions from the response
            matches = re.findall(r"Câu Hỏi Là:\s*(.+?)(?:\?|\.|\!|\n)", response)
            return [q.strip() + "?" for q in matches]
        except Exception as e:
            logger.error(f"Error generating NLU examples: {str(e)}")
            raise
    
    async def generate_nlu_examples_bulk(self, intents_data: List[dict]) -> Dict[int, List[str]]:
        """
        Generate NLU examples for multiple intents in bulk
        
        Args:
            intents_data: List of dictionaries with intent information
                Each dictionary should have: id, name/description, response_text
                
        Returns:
            Dictionary mapping intent_id to list of generated examples
        """
        system_message = {
            "role": "system", 
            "content": "Bạn là một trợ lý AI chuyên tạo câu hỏi mẫu cho chatbot. "
                      "Nhiệm vụ của bạn là tạo ra các câu hỏi đa dạng cho nhiều intent khác nhau "
                      "dựa trên thông tin được cung cấp."
        }
        
        # Prepare the content for the prompt
        intents_prompt = ""
        for i, intent in enumerate(intents_data):
            intent_id = intent.get("id")
            intent_name = intent.get("name") or intent.get("description") or f"Intent {intent_id}"
            response_text = intent.get("response_text", "")
            
            intents_prompt += f"INTENT #{i+1} [ID: {intent_id}]:\n"
            intents_prompt += f"Tên: {intent_name}\n"
            intents_prompt += f"Nội dung phản hồi: {response_text}\n\n"
        
        user_message = {
            "role": "user",
            "content": f"""Hãy tạo câu hỏi mẫu cho các intent sau đây:

{intents_prompt}

Yêu cầu:
1. Tạo ít nhất 5 câu hỏi cho mỗi intent.
2. Câu hỏi phải liên quan trực tiếp đến nội dung của intent.
3. Câu hỏi phải đa dạng về cách hỏi.
4. Câu hỏi phải tự nhiên như người dùng thực sự hỏi.
5. Định dạng kết quả như sau:

INTENT #1 [ID: <intent_id>]:
- Câu hỏi 1
- Câu hỏi 2
- Câu hỏi 3
...

INTENT #2 [ID: <intent_id>]:
- Câu hỏi 1
...

Vui lòng tạo câu hỏi cho tất cả các intent ngay bây giờ:"""
        }
        
        messages = [system_message, user_message]
        
        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=4000,  # Tăng max_tokens vì đây là bulk generation
                model=self.default_model
            )
            
            # Parse the response to extract questions for each intent
            result = {}
            current_intent_id = None
            current_questions = []
            
            # Regex pattern to match intent headers and questions
            intent_pattern = r"INTENT #\d+\s*\[ID:\s*(\d+)\]:"
            question_pattern = r"[-•]\s*(.+?)(?=\n[-•]|\n\s*\n|\n\s*INTENT|\Z)"
            
            # Find all intent sections
            intent_sections = re.split(intent_pattern, response)[1:]  # Skip the first empty element
            
            # Process each intent section
            for i in range(0, len(intent_sections), 2):
                if i + 1 < len(intent_sections):
                    intent_id = int(intent_sections[i])
                    questions_text = intent_sections[i + 1]
                    
                    # Extract questions from this section
                    questions = re.findall(question_pattern, questions_text, re.DOTALL)
                    questions = [q.strip() for q in questions if q.strip()]
                    
                    if questions:
                        result[intent_id] = questions
            
            return result
        except Exception as e:
            logger.error(f"Error generating bulk NLU examples: {str(e)}")
            raise
