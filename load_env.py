#!/usr/bin/env python3
"""
Script để tải biến môi trường từ file .env và sử dụng cho cả Rasa và FastAPI
"""
import os
import sys
from dotenv import load_dotenv
import argparse
import yaml
import json

def load_environment():
    """Tải biến môi trường từ file .env"""
    # Tải biến môi trường từ file .env
    load_dotenv()
    
    # Kiểm tra xem các biến môi trường cần thiết đã được tải chưa
    required_vars = [
        "POSTGRES_SERVER", 
        "POSTGRES_PORT", 
        "POSTGRES_USER", 
        "POSTGRES_PASSWORD", 
        "POSTGRES_DB",
        "RASA_SERVER",
        "RASA_ACTION_SERVER"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Lỗi: Các biến môi trường sau chưa được định nghĩa trong file .env: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("Đã tải biến môi trường từ file .env thành công.")

def update_rasa_endpoints():
    """Cập nhật file endpoints.yml của Rasa với biến môi trường"""
    # Đường dẫn đến file endpoints.yml
    endpoints_file = os.path.join("rasa", "endpoints.yml")
    
    # Đọc nội dung file
    with open(endpoints_file, "r") as file:
        endpoints = yaml.safe_load(file)
    
    # Cập nhật URL của action_endpoint
    action_server = os.getenv("RASA_ACTION_SERVER")
    if action_server and "action_endpoint" in endpoints:
        endpoints["action_endpoint"]["url"] = f"{action_server}/webhook"
    
    # Ghi lại file
    with open(endpoints_file, "w") as file:
        yaml.dump(endpoints, file, default_flow_style=False)
    
    print(f"Đã cập nhật {endpoints_file} với biến môi trường.")

def update_rasa_credentials():
    """Cập nhật file credentials.yml của Rasa với biến môi trường"""
    # Đường dẫn đến file credentials.yml
    credentials_file = os.path.join("rasa", "credentials.yml")
    
    # Đọc nội dung file
    with open(credentials_file, "r") as file:
        credentials = yaml.safe_load(file)
    
    # Cập nhật URL của REST webhook
    if "rest" in credentials:
        credentials["rest"] = {}  # Đảm bảo rest là một dictionary
    
    # Ghi lại file
    with open(credentials_file, "w") as file:
        yaml.dump(credentials, file, default_flow_style=False)
    
    print(f"Đã cập nhật {credentials_file} với biến môi trường.")

def main():
    parser = argparse.ArgumentParser(description="Tải biến môi trường từ file .env và cập nhật cấu hình")
    parser.add_argument("--update-rasa", action="store_true", help="Cập nhật cấu hình Rasa")
    args = parser.parse_args()
    
    # Tải biến môi trường
    load_environment()
    
    # Cập nhật cấu hình Rasa nếu được yêu cầu
    if args.update_rasa:
        update_rasa_endpoints()
        update_rasa_credentials()

if __name__ == "__main__":
    main()
