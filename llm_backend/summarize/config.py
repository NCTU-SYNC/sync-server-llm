from collections.abc import Callable, Sequence
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

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
DEFALUT_QUERY_STR = "請用繁體中文總結這幾篇新聞。"


class ContentFormat(StrEnum):
    PLAIN = "plain"
    NUMBERED = "numbered"


type ContentFormater = Callable[[Sequence[str]], Sequence[str]]

CONTENT_FORMATTERS: dict[ContentFormat, ContentFormater] = {
    ContentFormat.PLAIN: lambda x: x,
    ContentFormat.NUMBERED: lambda x: [
        f"{i}. {line}" for i, line in enumerate(x, start=1)
    ],
}


class ChatgptConfig(BaseModel):
    api_key: str


class SummarizeQueryConfig(BaseModel):
    system_template: str = DEFAULT_SYSTEM_TEMPLATE
    user_template: Annotated[
        str, AfterValidator(contains_placeholder("context_str", "query_str"))
    ] = DEFAULT_USER_TEMPLATE
    query_str: str = Field(
        DEFALUT_QUERY_STR,
        description="The content of `{query_str}` placeholder in the user template.",
    )
    content_format: ContentFormat = ContentFormat.PLAIN


class SummarizeConfig(BaseModel):
    chatgpt: ChatgptConfig
    query: SummarizeQueryConfig
