from typing import Any, Text, Dict, List, Type, Optional

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

# Import hàm preprocessing từ thư viện đã cài đặt
from vnpreprocess.utils.process import preprocessing as vn_preprocessing_function

@DefaultV1Recipe.register(
    component_types=[DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class VietnameseTextPreprocessor(GraphComponent):
    """
    A custom Rasa NLU component to preprocess Vietnamese text using
    the vnpreprocess.utils.process.preprocessing function.
    """

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initializes the preprocessor."""
        self._config = config

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "VietnameseTextPreprocessor":
        """Creates a new component."""
        return cls(config)

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {}

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Processes training data by applying vn_preprocessing_function to each example."""
        for example in training_data.training_examples:
            if text := example.get("text"): # Python 3.8+ walrus operator
                example.set("text", vn_preprocessing_function(text))
        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        """Processes incoming messages by applying vn_preprocessing_function to each message."""
        for msg in messages:
            if text := msg.get("text"): # Python 3.8+ walrus operator
                msg.set("text", vn_preprocessing_function(text))
        return messages
