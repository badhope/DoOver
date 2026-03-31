from langchain_core.language_models import BaseChatModel
from llm.client import load_active_llm

def get_model() -> BaseChatModel:
    return load_active_llm()
