import os

import grpc
from pydantic import BaseModel

from .rag import RagConfig, RagService, add_RagServiceServicer_to_server


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int
    max_workers: int = (os.cpu_count() or 1) * 5


class Config(BaseModel):
    server: ServerConfig
    service: RagConfig


def setup_rag_service(config: Config, server: grpc.aio.Server):
    rag_service = RagService(config.service)
    add_RagServiceServicer_to_server(rag_service, server)
