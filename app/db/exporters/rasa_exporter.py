#!/usr/bin/env python3
"""
Script để xuất dữ liệu từ cơ sở dữ liệu PostgreSQL thành các file Rasa
"""
import os
import sys
import yaml
import json
from sqlmodel import Session, select
from datetime import datetime
from typing import List, Dict, Any, Optional

# Thêm thư mục gốc vào sys.path để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.db.database import engine
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_nlu_example import RasaNluExample
from app.db.models.rasa_entity import RasaEntity
from app.db.models.rasa_domain_element import RasaDomainElement
from app.db.models.rasa_rule import RasaRule
from app.db.models.rasa_story import RasaStory
from app.core.config import settings

# Đường dẫn đến thư mục Rasa
RASA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "rasa")
RASA_DATA_DIR = os.path.join(RASA_DIR, "data")
NLU_FILE = os.path.join(RASA_DATA_DIR, "nlu.yml")
DOMAIN_FILE = os.path.join(RASA_DIR, "domain.yml")
RULES_FILE = os.path.join(RASA_DATA_DIR, "rules.yml")
STORIES_FILE = os.path.join(RASA_DATA_DIR, "stories.yml")

def ensure_dir_exists(directory):
    """
    Đảm bảo thư mục tồn tại
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

class RasaYamlDumper(yaml.SafeDumper):
    """
    Custom YAML Dumper để định dạng đúng cú pháp Rasa
    """
    def represent_list(self, data):
        # Xử lý đặc biệt cho danh sách examples
        if len(data) > 0 and isinstance(data[0], str) and any(item.startswith('- ') for item in data):
            # Đây là danh sách examples, giữ nguyên định dạng
            return self.represent_scalar('tag:yaml.org,2002:str', '\n'.join(data), style='|')
        return super().represent_sequence('tag:yaml.org,2002:seq', data)

def write_yaml_file(file_path, data):
    """
    Ghi dữ liệu vào file YAML với định dạng phù hợp cho Rasa
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False, Dumper=RasaYamlDumper)
        print(f"Đã ghi file {file_path}")
    except Exception as e:
        print(f"Lỗi khi ghi file {file_path}: {e}")

def export_nlu(session):
    """
    Xuất dữ liệu NLU từ cơ sở dữ liệu thành file nlu.yml
    """
    print("Đang xuất dữ liệu NLU...")
    
    # Lấy tất cả intent và ví dụ NLU
    intents = session.exec(select(RasaIntent).where(RasaIntent.is_active == True)).all()
    
    nlu_data = {
        "version": "3.1",
        "nlu": []
    }
    
    for intent in intents:
        # Lấy các ví dụ NLU cho intent này
        examples = session.exec(
            select(RasaNluExample)
            .where(RasaNluExample.intent_id == intent.id)
            .where(RasaNluExample.is_active == True)
        ).all()
        
        if not examples:
            continue
        
        # Tạo danh sách examples riêng biệt thay vì chuỗi
        examples_list = []
        for example in examples:
            examples_list.append(f"- {example.text}")
        
        # Thêm vào dữ liệu NLU
        nlu_data["nlu"].append({
            "intent": intent.name,
            "examples": examples_list
        })
    
    # Lấy tất cả entities
    entities = session.exec(select(RasaEntity).where(RasaEntity.is_active == True)).all()
    if entities:
        nlu_data["entities"] = [entity.name for entity in entities]
    
    # Ghi file nlu.yml
    ensure_dir_exists(RASA_DATA_DIR)
    write_yaml_file(NLU_FILE, nlu_data)
    print(f"Đã xuất {len(nlu_data['nlu'])} intent với ví dụ NLU và {len(entities)} entities")

def export_domain(session):
    """
    Xuất dữ liệu domain từ cơ sở dữ liệu thành file domain.yml
    """
    print("Đang xuất dữ liệu domain...")
    
    # Lấy tất cả intent, entity, response
    intents = session.exec(select(RasaIntent).where(RasaIntent.is_active == True)).all()
    entities = session.exec(select(RasaEntity).where(RasaEntity.is_active == True)).all()
    
    # Tạo dữ liệu domain
    domain_data = {
        "version": "3.1",
        "intents": [intent.name for intent in intents],
        "entities": [entity.name for entity in entities],
        "responses": {}
    }
    
    # Thêm responses
    for intent in intents:
        responses = session.exec(
            select(RasaResponse)
            .where(RasaResponse.intent_id == intent.id)
            .where(RasaResponse.is_active == True)
        ).all()
        
        for response in responses:
            # Sửa tên response để khớp với định dạng gốc (utter_ask_*)
            response_key = f"utter_ask_{intent.name.replace('hoi_', '')}" if intent.name.startswith('hoi_') else f"utter_{intent.name}"
            
            if response_key not in domain_data["responses"]:
                domain_data["responses"][response_key] = []
            
            response_obj = {"text": response.response_text}
            
            # Thêm metadata nếu có
            if response.meta_data:
                try:
                    metadata = json.loads(response.meta_data)
                    for key, value in metadata.items():
                        response_obj[key] = value
                except:
                    pass
            
            domain_data["responses"][response_key].append(response_obj)
    
    # Thêm domain elements (slots, forms, etc.)
    domain_elements = session.exec(
        select(RasaDomainElement).where(RasaDomainElement.is_active == True)
    ).all()
    
    # Nhóm domain elements theo loại
    element_types = {}
    for element in domain_elements:
        if element.element_type not in element_types:
            element_types[element.element_type] = {}
        
        # Parse configuration
        try:
            config = yaml.safe_load(element.configuration) if element.configuration else {}
        except:
            config = {}
        
        element_types[element.element_type][element.name] = config
    
    # Thêm vào domain data
    for element_type, elements in element_types.items():
        domain_data[element_type] = elements
    
    # Thêm actions sử dụng tên response đã điều chỉnh
    domain_data["actions"] = []
    for intent in intents:
        action_name = f"utter_ask_{intent.name.replace('hoi_', '')}" if intent.name.startswith('hoi_') else f"utter_{intent.name}"
        domain_data["actions"].append(action_name)
    
    # Thêm các custom actions từ rules và stories nếu có
    custom_actions = set()
    
    # Ghi file domain.yml
    write_yaml_file(DOMAIN_FILE, domain_data)
    print(f"Đã xuất domain với {len(domain_data['intents'])} intents, {len(domain_data['entities'])} entities, {len(domain_data['responses'])} responses")

def export_rules(session):
    """
    Xuất dữ liệu rules từ cơ sở dữ liệu thành file rules.yml
    """
    print("Đang xuất dữ liệu rules...")
    
    # Lấy rules từ database
    db_rules = session.exec(select(RasaRule).where(RasaRule.is_active == True)).all()
    
    # Tạo dữ liệu rules
    rules_data = {
        "version": "3.1",
        "rules": []
    }
    
    # Thêm rules từ database
    for rule in db_rules:
        try:
            # Parse rule_content thành dict
            rule_dict = yaml.safe_load(rule.rule_content)
            if rule_dict:
                rules_data["rules"].append(rule_dict)
        except Exception as e:
            print(f"Lỗi khi parse rule {rule.id}: {e}")
    
    # Nếu không có rules từ database, thêm rules mặc định
    if not rules_data["rules"]:
        rules_data["rules"] = [
            {
                "rule": "Chào hỏi",
                "steps": [
                    {"intent": "greet"},
                    {"action": "utter_greet"}
                ]
            },
            {
                "rule": "Kết thúc hội thoại",
                "steps": [
                    {"intent": "goodbye"},
                    {"action": "utter_goodbye"}
                ]
            },
            {
                "rule": "fallback",
                "steps": [
                    {"intent": "nlu_fallback"},
                    {"action": "utter_default"}
                ]
            }
        ]
    
    # Ghi file rules.yml
    ensure_dir_exists(RASA_DATA_DIR)
    write_yaml_file(RULES_FILE, rules_data)
    print(f"Đã xuất {len(rules_data['rules'])} rules")

def export_stories(session):
    """
    Xuất dữ liệu stories từ cơ sở dữ liệu thành file stories.yml
    """
    print("Đang xuất dữ liệu stories...")
    
    # Lấy stories từ database
    db_stories = session.exec(select(RasaStory).where(RasaStory.is_active == True)).all()
    
    # Tạo dữ liệu stories
    stories_data = {
        "version": "3.1",
        "stories": []
    }
    
    # Thêm stories từ database
    for story in db_stories:
        try:
            # Parse story_content thành dict
            story_dict = yaml.safe_load(story.story_content)
            if story_dict:
                stories_data["stories"].append(story_dict)
        except Exception as e:
            print(f"Lỗi khi parse story {story.id}: {e}")
    
    # Nếu không có stories từ database, thêm stories mặc định
    if not stories_data["stories"]:
        stories_data["stories"] = [
            {
                "story": "Hỏi về danh sách ngành và chỉ tiêu chung",
                "steps": [
                    {"intent": "greet"},
                    {"action": "utter_greet"},
                    {"intent": "hoi_danh_sach_nganh"},
                    {"action": "utter_ask_nganh"},
                    {"intent": "hoi_chi_tieu_chung"},
                    {"action": "utter_ask_chi_tieu_chung"}
                ]
            },
            {
                "story": "Hỏi về điều kiện và miễn ngoại ngữ",
                "steps": [
                    {"intent": "hoi_dieu_kien_du_tuyen"},
                    {"action": "utter_ask_dieu_kien"},
                    {"intent": "hoi_mien_ngoai_ngu"},
                    {"action": "utter_ask_mien_ngoai_ngu"}
                ]
            }
        ]
    
    # Ghi file stories.yml
    ensure_dir_exists(RASA_DATA_DIR)
    write_yaml_file(STORIES_FILE, stories_data)
    print(f"Đã xuất {len(stories_data['stories'])} stories")

def main():
    """
    Hàm chính để chạy exporter
    """
    print("Bắt đầu xuất dữ liệu từ cơ sở dữ liệu thành các file Rasa...")
    
    # Tạo session
    with Session(engine) as session:
        # Xuất dữ liệu
        export_nlu(session)
        export_domain(session)
        export_rules(session)
        export_stories(session)
    
    print("Hoàn thành xuất dữ liệu!")

if __name__ == "__main__":
    main()
