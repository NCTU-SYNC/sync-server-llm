from collections.abc import Callable, Sequence

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

from .config import ContentFormat, SummarizeConfig

__all__ = [
    "SummarizeService",
    "add_SummarizeServiceServicer_to_server",
]


type ContentFormatter = Callable[[Sequence[str]], Sequence[str]]

CONTENT_FORMATTERS: dict[ContentFormat, ContentFormatter] = {
    ContentFormat.PLAIN: lambda x: x,
    ContentFormat.NUMBERED: lambda x: [
        f"{i}. {line}" for i, line in enumerate(x, start=1)
    ],
}


class SummarizeService(summarize_pb2_grpc.SummarizeServiceServicer):
    def __init__(
        self,
        config: SummarizeConfig,
    ):
        llm = OpenAI(model=config.chatgpt.model, api_key=config.chatgpt.api_key)

        self.summarizer = get_response_synthesizer(
            llm, response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True
        )
        summarizer_prompt = ChatPromptTemplate(
            message_templates=[
                ChatMessage(
                    role=MessageRole.SYSTEM, content=config.query.system_template
                ),
                ChatMessage(role=MessageRole.USER, content=config.query.user_template),
            ],
            prompt_type=PromptType.SUMMARY,
        )
        self.summarizer.update_prompts({"summary_template": summarizer_prompt})

        self.query_str = config.query.query_str
        self.content_formatter = CONTENT_FORMATTERS[config.query.content_format]

    async def Summarize(
        self,
        request: summarize_pb2.SummarizeRequest,
        context: grpc.aio.ServicerContext,
    ):
        texts = self.content_formatter(request.contents)
        summary = str(self.summarizer.aget_response(self.query_str, texts))
        return summarize_pb2.SummarizeResponse(summary=summary)
