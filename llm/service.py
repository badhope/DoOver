from langchain_core.language_models import BaseChatModel
from llm.client import load_active_llm
from loguru import logger

from tools.registry import active_tools
def get_model() -> BaseChatModel:
    try:
        model = load_active_llm()
        return model
    except Exception as e:
        logger.error(f"Failed to load active llm: {e}")
        raise

