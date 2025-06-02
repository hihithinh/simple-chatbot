from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ChatbotInteractionBase(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    user_message: str
    bot_response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    meta_data: Optional[str] = None

class ChatbotInteractionCreate(ChatbotInteractionBase):
    pass

class ChatbotInteractionInDBBase(ChatbotInteractionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatbotInteraction(ChatbotInteractionInDBBase):
    pass

class ChatbotInteractionWithParsedResponse(ChatbotInteraction):
    parsed_response: List[Dict[str, Any]] = []
    
    @staticmethod
    def from_db_model(db_model):
        import json
        interaction = ChatbotInteraction.from_orm(db_model)
        interaction_dict = interaction.dict()
        
        # Parse bot_response từ JSON string thành list
        try:
            if interaction.bot_response:
                interaction_dict["parsed_response"] = json.loads(interaction.bot_response)
        except:
            interaction_dict["parsed_response"] = []
            
        # Parse meta_data từ JSON string thành dict
        try:
            if interaction.meta_data:
                interaction_dict["parsed_meta_data"] = json.loads(interaction.meta_data)
        except:
            interaction_dict["parsed_meta_data"] = {}
            
        return ChatbotInteractionWithParsedResponse(**interaction_dict)
