import os

from grpc._server import _Server
from pydantic import BaseModel

from .search import (
    SearchService,
    add_SearchServiceServicer_to_server,
)
from .search.config import SearchConfig
from .summarize import (
    SummarizeService,
    add_SummarizeServiceServicer_to_server,
)
from .summarize.config import SummarizeConfig


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int
    max_workers: int = (os.cpu_count() or 1) * 5


class ServiceConfig(BaseModel):
    search: SearchConfig
    summarize: SummarizeConfig


class Config(BaseModel):
    server: ServerConfig
    service: ServiceConfig


def setup_search_service(config: Config, server: _Server):
    search_service = SearchService(config.service.search)
    add_SearchServiceServicer_to_server(search_service, server)


def setup_summarize_service(config: Config, server: _Server):
    summarize_service = SummarizeService(config.service.summarize)
    add_SummarizeServiceServicer_to_server(summarize_service, server)
