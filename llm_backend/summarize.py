from typing import Optional

import grpc
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.core.llms import MessageRole
from llama_index.core.prompts import PromptType
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.llms.openai import OpenAI

from llm_backend.grpc import summarize_pb2
from llm_backend.grpc import summarize_pb2_grpc
from llm_backend.grpc.summarize_pb2_grpc import \
    add_SummarizeServiceServicer_to_server

__all__ = [
    'SummarizeService',
    'add_SummarizeServiceServicer_to_server',
]

DEFAULT_SYSTEM_TEMPLATE = (
    'You are an expert Q&A system that is trusted around the world.\n'
    'Always answer the query using the provided context information,'
    'and not prior knowledge.\n'
    'Some rules to follow:\n'
    '1. Never directly reference the given context in your answer.\n'
    "2. Avoid statements like 'Based on the context, ...' or"
    "The context information ...' or anything along"
    'those lines.')

DEFAULT_USER_TEMPLATE = (
    'Context information from multiple sources is below.\n'
    '---------------------\n'
    '{context_str}\n'
    '---------------------\n'
    'Given the information from multiple sources and not prior knowledge,'
    'answer the query.\n'
    'Query: {query_str}\n'
    'Answer:')

DEFALUT_SUMMARIZE_QUERY_STR = '請用繁體中文總結這幾篇新聞。'


class SummarizeService(summarize_pb2_grpc.SummarizeServiceServicer):

    def __init__(self,
                 api_key: str,
                 system_template: Optional[str] = None,
                 user_template: Optional[str] = None,
                 query_str: Optional[str] = None):
        llm = OpenAI(api_key=api_key)

        self.summarizer = get_response_synthesizer(
            llm, response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True)
        summarizer_prompt = ChatPromptTemplate(
            message_templates=[
                ChatMessage(role=MessageRole.SYSTEM,
                            content=system_template or DEFAULT_SYSTEM_TEMPLATE),
                ChatMessage(role=MessageRole.USER,
                            content=user_template or DEFAULT_USER_TEMPLATE),
            ],
            prompt_type=PromptType.SUMMARY,
        )
        self.summarizer.update_prompts({'summary_template': summarizer_prompt})

        self.query_str = query_str or DEFALUT_SUMMARIZE_QUERY_STR

    def Summarize(
        self,
        request: summarize_pb2.SummarizeRequest,
        _context: grpc.ServicerContext,
    ):
        texts = request.contents
        summary = str(self.summarizer.get_response(self.query_str, texts))
        return summarize_pb2.SummarizeResponse(summary=summary)
