from fastapi import APIRouter

from app.api.api_v1.endpoints import intents, responses, nlu_examples, rasa, data_sources, qa_generator

api_router = APIRouter()
api_router.include_router(intents.router, prefix="/intents", tags=["intents"])
api_router.include_router(responses.router, prefix="/responses", tags=["responses"])
api_router.include_router(nlu_examples.router, prefix="/nlu-examples", tags=["nlu-examples"])
api_router.include_router(rasa.router, prefix="/rasa", tags=["rasa"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(qa_generator.router, prefix="/qa-generator", tags=["qa-generator"])
