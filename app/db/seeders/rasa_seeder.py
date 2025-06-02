#!/usr/bin/env python3
"""
Script để nhập dữ liệu từ các file Rasa vào cơ sở dữ liệu PostgreSQL
"""
import os
import sys
import yaml
import re
from sqlmodel import Session, select
from datetime import datetime

# Thêm thư mục gốc vào sys.path để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.db.database import engine, create_db_and_tables
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_nlu_example import RasaNluExample
from app.db.models.rasa_entity import RasaEntity
from app.db.models.rasa_domain_element import RasaDomainElement
from app.db.models.rasa_rule import RasaRule
from app.db.models.rasa_story import RasaStory
from app.core.config import settings

# Đường dẫn đến các file Rasa
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
RASA_DATA_DIR = os.path.join(SEEDER_DIR, "rasa_data")
NLU_FILE = os.path.join(RASA_DATA_DIR, "nlu.yml")
DOMAIN_FILE = os.path.join(RASA_DATA_DIR, "domain.yml")
RULES_FILE = os.path.join(RASA_DATA_DIR, "rules.yml")
STORIES_FILE = os.path.join(RASA_DATA_DIR, "stories.yml")

def load_yaml_file(file_path):
    """
    Đọc file YAML và trả về dữ liệu
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return None

def extract_entities_from_example(example):
    """
    Trích xuất các entity từ ví dụ NLU
    """
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    entities = []
    
    for match in re.finditer(pattern, example):
        entity_value = match.group(1)
        entity_name = match.group(2)
        entities.append({
            "entity": entity_name,
            "value": entity_value,
            "start": match.start(),
            "end": match.end()
        })
    
    return entities

def clean_example_text(example):
    """
    Làm sạch văn bản ví dụ bằng cách loại bỏ các thẻ entity
    """
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.sub(pattern, r'\1', example)

def seed_intents(session):
    """
    Nhập dữ liệu intents từ domain.yml
    """
    print("Đang nhập dữ liệu intents...")
    domain_data = load_yaml_file(DOMAIN_FILE)
    
    if not domain_data or 'intents' not in domain_data:
        print("Không tìm thấy intents trong domain.yml")
        return
    
    # Thêm dữ liệu mới
    for intent_name in domain_data['intents']:
        # Nếu intent là một dict, lấy tên từ key đầu tiên
        if isinstance(intent_name, dict):
            intent_name = list(intent_name.keys())[0]
        
        intent = RasaIntent(
            name=intent_name,
            description=f"Intent {intent_name}",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(intent)
    
    session.commit()
    print(f"Đã nhập {len(domain_data['intents'])} intents")

def seed_responses(session):
    """
    Nhập dữ liệu responses từ domain.yml
    """
    print("Đang nhập dữ liệu responses...")
    domain_data = load_yaml_file(DOMAIN_FILE)
    
    if not domain_data or 'responses' not in domain_data:
        print("Không tìm thấy responses trong domain.yml")
        return
    
    # Lấy mapping của intent
    intent_map = {}
    for intent in session.exec(select(RasaIntent)).all():
        intent_map[intent.name] = intent.id
    
    # Thêm dữ liệu mới
    response_count = 0
    for response_key, responses in domain_data['responses'].items():
        # Lấy intent name từ response key (utter_ask_xxx -> hoi_xxx)
        intent_name = None
        if response_key.startswith('utter_ask_'):
            intent_name = 'hoi_' + response_key[10:]
        elif response_key.startswith('utter_'):
            intent_name = response_key[6:]
        
        # Nếu không tìm thấy intent tương ứng, bỏ qua
        if intent_name not in intent_map:
            print(f"Không tìm thấy intent cho response {response_key}")
            continue
        
        intent_id = intent_map[intent_name]
        
        for response in responses:
            if 'text' in response:
                response_obj = RasaResponse(
                    intent_id=intent_id,
                    response_text=response['text'],
                    response_type='text',
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(response_obj)
                response_count += 1
    
    session.commit()
    print(f"Đã nhập {response_count} responses")

def seed_nlu_examples(session):
    """
    Nhập dữ liệu NLU examples từ nlu.yml
    """
    print("Đang nhập dữ liệu NLU examples...")
    nlu_data = load_yaml_file(NLU_FILE)
    
    if not nlu_data or 'nlu' not in nlu_data:
        print("Không tìm thấy NLU examples trong nlu.yml")
        return
    
    # Lấy mapping của intent
    intent_map = {}
    for intent in session.exec(select(RasaIntent)).all():
        intent_map[intent.name] = intent.id
    
    # Thêm dữ liệu mới
    example_count = 0
    for item in nlu_data['nlu']:
        if 'intent' not in item or 'examples' not in item:
            continue
        
        intent_name = item['intent']
        if intent_name not in intent_map:
            print(f"Không tìm thấy intent {intent_name} trong cơ sở dữ liệu")
            continue
        
        intent_id = intent_map[intent_name]
        examples = item['examples'].strip().split('\n')
        
        for example in examples:
            # Loại bỏ dấu - ở đầu và khoảng trắng
            example = example.strip()
            if example.startswith('- '):
                example = example[2:]
            
            # Làm sạch văn bản ví dụ
            clean_text = clean_example_text(example)
            
            # Thêm ví dụ vào cơ sở dữ liệu
            nlu_example = RasaNluExample(
                intent_id=intent_id,
                text=clean_text,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(nlu_example)
            example_count += 1
    
    session.commit()
    print(f"Đã nhập {example_count} NLU examples")

def seed_entities(session):
    """
    Nhập dữ liệu entities từ domain.yml
    """
    print("Đang nhập dữ liệu entities...")
    domain_data = load_yaml_file(DOMAIN_FILE)
    
    if not domain_data or 'entities' not in domain_data:
        print("Không tìm thấy entities trong domain.yml")
        return
    
    # Thêm dữ liệu mới
    for entity_name in domain_data['entities']:
        entity = RasaEntity(
            name=entity_name,
            description=f"Entity {entity_name}",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(entity)
    
    session.commit()
    print(f"Đã nhập {len(domain_data['entities'])} entities")

def seed_domain_elements(session):
    """
    Nhập dữ liệu domain elements từ domain.yml
    """
    print("Đang nhập dữ liệu domain elements...")
    domain_data = load_yaml_file(DOMAIN_FILE)
    
    if not domain_data:
        print("Không tìm thấy dữ liệu trong domain.yml")
        return
    
    # Thêm dữ liệu mới
    element_count = 0
    for element_type, elements in domain_data.items():
        if element_type in ['version', 'intents', 'entities', 'responses', 'actions', 'forms', 'e2e_actions']:
            continue
        
        if isinstance(elements, list):
            for element in elements:
                if isinstance(element, dict):
                    for name, data in element.items():
                        domain_element = RasaDomainElement(
                            element_type=element_type,
                            name=name,
                            configuration=yaml.dump(data),
                            description=f"{element_type}: {name}",
                            is_active=True,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        session.add(domain_element)
                        element_count += 1
                else:
                    domain_element = RasaDomainElement(
                        element_type=element_type,
                        name=str(element),
                        configuration="{}",
                        description=f"{element_type}: {element}",
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(domain_element)
                    element_count += 1
        elif isinstance(elements, dict):
            for name, data in elements.items():
                domain_element = RasaDomainElement(
                    element_type=element_type,
                    name=name,
                    configuration=yaml.dump(data),
                    description=f"{element_type}: {name}",
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(domain_element)
                element_count += 1
    
    session.commit()
    print(f"Đã nhập {element_count} domain elements")

def seed_rules(session):
    """
    Nhập dữ liệu rules từ rules.yml
    """
    print("Đang nhập dữ liệu rules...")
    rules_data = load_yaml_file(RULES_FILE)
    
    if not rules_data or 'rules' not in rules_data:
        print("Không tìm thấy rules trong rules.yml")
        return
    
    # Thêm dữ liệu mới
    rule_count = 0
    for rule in rules_data['rules']:
        rule_name = rule.get('rule', f"Rule {rule_count + 1}")
        
        # Chuyển rule thành chuỗi YAML
        rule_content = yaml.dump(rule, default_flow_style=False, allow_unicode=True)
        
        # Thêm rule vào cơ sở dữ liệu
        rule_obj = RasaRule(
            name=rule_name,
            rule_content=rule_content,
            description=f"Rule: {rule_name}",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(rule_obj)
        rule_count += 1
    
    session.commit()
    print(f"Đã nhập {rule_count} rules")

def seed_stories(session):
    """
    Nhập dữ liệu stories từ stories.yml
    """
    print("Đang nhập dữ liệu stories...")
    stories_data = load_yaml_file(STORIES_FILE)
    
    if not stories_data or 'stories' not in stories_data:
        print("Không tìm thấy stories trong stories.yml")
        return
    
    # Thêm dữ liệu mới
    story_count = 0
    for story in stories_data['stories']:
        story_name = story.get('story', f"Story {story_count + 1}")
        
        # Chuyển story thành chuỗi YAML
        story_content = yaml.dump(story, default_flow_style=False, allow_unicode=True)
        
        # Thêm story vào cơ sở dữ liệu
        story_obj = RasaStory(
            name=story_name,
            story_content=story_content,
            description=f"Story: {story_name}",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(story_obj)
        story_count += 1
    
    session.commit()
    print(f"Đã nhập {story_count} stories")

def main():
    """
    Hàm chính để chạy seeder
    """
    print("Bắt đầu nhập dữ liệu từ Rasa vào cơ sở dữ liệu...")
    
    # Tạo bảng nếu chưa tồn tại
    create_db_and_tables()
    
    # Tạo session
    with Session(engine) as session:
        # Xóa dữ liệu cũ theo thứ tự để tránh vi phạm ràng buộc khóa ngoại
        print("Đang xóa dữ liệu cũ...")
        session.query(RasaNluExample).delete()
        session.query(RasaResponse).delete()
        session.query(RasaDomainElement).delete()
        session.query(RasaEntity).delete()
        session.query(RasaRule).delete()
        session.query(RasaStory).delete()
        session.query(RasaIntent).delete()
        session.commit()
        
        # Nhập dữ liệu mới
        seed_intents(session)
        seed_responses(session)
        seed_nlu_examples(session)
        seed_entities(session)
        seed_domain_elements(session)
        seed_rules(session)
        seed_stories(session)
    
    print("Hoàn thành nhập dữ liệu!")

if __name__ == "__main__":
    main()
