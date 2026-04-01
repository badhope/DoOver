from pydantic import BaseModel, Field


class search_from_tavily_field_info(BaseModel):
    query: str = Field(
        description="Search keywords or query phrases. "
                    "Used to retrieve the latest information, news, facts, or data from the internet. "
                    "Please ensure that the keywords are specific and clear."
    )
    tavily_api_key: str = Field(
        description="Travis API key. "
                    "Yep, this parameter is not mandatory; "
                    "if not provided, the system will by default read from the configuration file. "
    )
