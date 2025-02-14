from enum import StrEnum
from typing import Annotated

from llama_index.llms.openai.utils import ALL_AVAILABLE_MODELS
from pydantic import AfterValidator, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..utils import contains_placeholder

DEFAULT_SYSTEM_TEMPLATE = (
    "You are an expert Q&A system that is trusted around the world.\n"
    "Always answer the query using the provided context information,"
    "and not prior knowledge.\n"
    "Some rules to follow:\n"
    "1. Never directly reference the given context in your answer.\n"
    "2. Avoid statements like 'Based on the context, ...' or"
    "The context information ...' or anything along"
    "those lines."
)
DEFAULT_USER_TEMPLATE = (
    "Context information from multiple sources is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the information from multiple sources and not prior knowledge,"
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer:"
)
DEFAULT_QUERY_STR = "請用繁體中文總結這幾篇新聞。"


class ContentFormat(StrEnum):
    PLAIN = "plain"
    NUMBERED = "numbered"


def is_available_model(model_name: str):
    if model_name not in ALL_AVAILABLE_MODELS:
        raise ValueError(
            f"Model {model_name} is not available. Available models are: {ALL_AVAILABLE_MODELS}"
        )
    return model_name


class ChatgptConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    api_key: str = Field(validation_alias="OPENAI_API_KEY")
    model: Annotated[
        str,
        Field("gpt-3.5-turbo"),
        AfterValidator(is_available_model),
    ]


class SummarizeQueryConfig(BaseModel):
    system_template: str = DEFAULT_SYSTEM_TEMPLATE
    user_template: Annotated[
        str, AfterValidator(contains_placeholder("context_str", "query_str"))
    ] = DEFAULT_USER_TEMPLATE
    query_str: str = Field(
        DEFAULT_QUERY_STR,
        description="The content of `{query_str}` placeholder in the user template.",
    )
    content_format: ContentFormat = ContentFormat.PLAIN


class SummarizeConfig(BaseModel):
    chatgpt: ChatgptConfig
    query: SummarizeQueryConfig
