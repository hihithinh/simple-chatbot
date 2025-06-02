# Import các model để Alembic có thể phát hiện
from app.db.models.data_source import DataSource
from app.db.models.crawled_content import CrawledContent
from app.db.models.rasa_intent import RasaIntent
from app.db.models.rasa_nlu_example import RasaNluExample
from app.db.models.rasa_response import RasaResponse
from app.db.models.rasa_story import RasaStory
from app.db.models.rasa_rule import RasaRule
from app.db.models.rasa_entity import RasaEntity
from app.db.models.rasa_domain_element import RasaDomainElement
from app.db.models.chatbot_interaction_log import ChatbotInteractionLog
