from collections.abc import Callable
from enum import StrEnum
from typing import Literal, Optional

import grpc
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import PromptType
from llama_index.core.response_synthesizers import (
    ResponseMode,
    get_response_synthesizer,
)
from llama_index.llms.openai import OpenAI

from llm_backend.protos import summarize_pb2, summarize_pb2_grpc
from llm_backend.protos.summarize_pb2_grpc import add_SummarizeServiceServicer_to_server

__all__ = [
    "SummarizeService",
    "add_SummarizeServiceServicer_to_server",
]

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

DEFALUT_SUMMARIZE_QUERY_STR = "請用繁體中文總結這幾篇新聞。"


class ContentFormat(StrEnum):
    PLAIN = "plain"
    NUMBERED = "numbered"


CONTENT_FORMATTERS: dict[ContentFormat, Callable[[list[str]], list[str]]] = {
    ContentFormat.PLAIN: lambda x: x,
    ContentFormat.NUMBERED: lambda x: [
        f"{i}. {line}" for i, line in enumerate(x, start=1)
    ],
}


class SummarizeService(summarize_pb2_grpc.SummarizeServiceServicer):
    def __init__(
        self,
        api_key: str,
        system_template: Optional[str] = None,
        user_template: Optional[str] = None,
        query_str: Optional[str] = None,
        content_format: ContentFormat | Literal["plain", "numbered"] = "plain",
    ):
        llm = OpenAI(api_key=api_key)

        self.summarizer = get_response_synthesizer(
            llm, response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True
        )
        summarizer_prompt = ChatPromptTemplate(
            message_templates=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=system_template or DEFAULT_SYSTEM_TEMPLATE,
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=user_template or DEFAULT_USER_TEMPLATE,
                ),
            ],
            prompt_type=PromptType.SUMMARY,
        )
        self.summarizer.update_prompts({"summary_template": summarizer_prompt})

        self.query_str = query_str or DEFALUT_SUMMARIZE_QUERY_STR
        self.content_formatter = CONTENT_FORMATTERS[ContentFormat(content_format)]

    def Summarize(
        self,
        request: summarize_pb2.SummarizeRequest,
        _context: grpc.ServicerContext,
    ):
        texts = self.content_formatter(request.contents)
        summary = str(self.summarizer.get_response(self.query_str, texts))
        return summarize_pb2.SummarizeResponse(summary=summary)
