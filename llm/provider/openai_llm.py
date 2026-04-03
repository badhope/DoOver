from langchain_openai import ChatOpenAI


def create_openai_llm(model_name, api_key, base_url, custom_headers=None,stream_usage=True):
    custom_headers = {
        "User-Agent": "curl/7.84.0",
    }

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        default_headers=custom_headers,
        streaming=stream_usage
    )
