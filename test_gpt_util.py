#!/usr/bin/env python3
import asyncio
import sys
import os
import json
from app.utils.gpt_util import GPTUtil
from app.core.config import settings
from app.api.api_v1.endpoints.qa_generator import create_list_dictionary

async def test_extract_key_points():
    """Test the GPT utility to extract key points in CSV format with descriptive titles"""
    util = GPTUtil(settings.OPENAI_API_KEY)
    
    # Sample text about UIT university
    sample_text = """
    Trường Đại học Công nghệ Thông tin (UIT) – ĐHQG-HCM thông báo tuyển sinh trình độ thạc sĩ đợt 1 năm 2023 với các ngành và chỉ tiêu như sau: 
    Khoa học máy tính: 60 chỉ tiêu, 
    Công nghệ thông tin: 60 chỉ tiêu, 
    Hệ thống thông tin: 30 chỉ tiêu, 
    Kỹ thuật phần mềm: 30 chỉ tiêu, 
    An toàn thông tin: 30 chỉ tiêu, 
    Khoa học dữ liệu: 30 chỉ tiêu. 
    
    Điều kiện dự tuyển: Thí sinh phải có bằng tốt nghiệp đại học ngành đúng, ngành phù hợp hoặc ngành gần với ngành đăng ký dự thi. 
    
    Thời gian đào tạo: 2 năm. 
    
    Địa điểm đào tạo: Trường Đại học Công nghệ Thông tin, Khu phố 6, P. Linh Trung, TP. Thủ Đức, TP. Hồ Chí Minh. 
    
    Lệ phí: Đăng ký dự thi: 200.000đ/thí sinh/hồ sơ, Dự thi: 300.000đ/môn thi. 
    
    Hình thức đăng ký: Thí sinh đăng ký dự thi trực tuyến tại website: http://tuyensinh.uit.edu.vn, sau đó nộp hồ sơ về Phòng Đào tạo Sau đại học và Khoa học Công nghệ, Trường Đại học Công nghệ Thông tin.
    """
    
    # Thêm một đoạn văn bản mới có một số thông tin trùng lặp và một số thông tin mới
    additional_text = """
    Trường Đại học Công nghệ Thông tin (UIT) – ĐHQG-HCM thông báo về việc tổ chức thi tuyển sinh trình độ thạc sĩ đợt 1 năm 2023.
    
    Thời gian thi: Dự kiến tháng 5/2023.
    
    Môn thi: 
    - Môn cơ bản: Toán cao cấp
    - Môn cơ sở: Tin học cơ sở
    - Môn ngoại ngữ: Tiếng Anh (có thể được miễn thi nếu có chứng chỉ theo quy định)
    
    Hình thức thi: Thi tự luận, thời gian 150 phút cho mỗi môn.
    
    Điều kiện miễn thi ngoại ngữ: Thí sinh có chứng chỉ tiếng Anh TOEFL iBT từ 46, TOEFL ITP từ 450, IELTS từ 5.5, TOEIC từ 600 trở lên hoặc các chứng chỉ khác theo quy định.
    
    Thời gian nhận hồ sơ: Từ ngày 01/03/2023 đến ngày 31/03/2023.
    """
    
    print("Trích xuất điểm thông tin từ đoạn văn đầu tiên...")
    result1 = await util.extract_key_points(sample_text, 5)
    print("\nKết quả GPT (đoạn 1):")
    print(result1)
    
    # Phân tích kết quả đầu tiên để lấy danh sách các điểm đã trích xuất
    key_points1 = util.extract_points_from_result(result1)
    print(f"\nĐã trích xuất {len(key_points1)} điểm thông tin từ đoạn 1")
    
    print("\nTrích xuất điểm thông tin từ đoạn văn thứ hai (với danh sách điểm đã trích xuất)...")
    # Truyền danh sách điểm đã trích xuất để tránh trùng lặp
    result2 = await util.extract_key_points_from_chunk(additional_text, 3, key_points1)
    print("\nKết quả GPT (đoạn 2):")
    print(result2)
    
    # Phân tích kết quả thứ hai
    key_points2 = util.extract_points_from_result(result2)
    print(f"\nĐã trích xuất {len(key_points2)} điểm thông tin từ đoạn 2")
    
    # Kết hợp tất cả các điểm thông tin
    all_points = key_points1 + key_points2
    
    print("\nTất cả các điểm thông tin đã trích xuất:")
    print(json.dumps(all_points, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_extract_key_points())
