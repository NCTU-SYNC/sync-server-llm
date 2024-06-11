import argparse
import logging
import os
import sys
from concurrent import futures
from typing import Any

import grpc
import tomllib

from llm_backend import search, summarize

CONFIG = dict[str, Any]


def create_search_service(config: CONFIG):
    search_config: CONFIG = config.get("service", {}).get("search", {})
    return search.SearchService(
        host=search_config.get("chromadb", {}).get("host"),
        port=search_config.get("chromadb", {}).get("port"),
        token=search_config.get("chromadb", {}).get("token"),
        collection=search_config.get("chromadb", {}).get("collection"),
        embedding_model=search_config.get("embeddings", {}).get("model"),
        query_template=search_config.get("query", {}).get("prompt_template"),
        similarity_top_k=search_config.get("query", {}).get("similarity_top_k"),
    )


def create_summarize_service(config: CONFIG):
    summarize_config: CONFIG = config.get("service", {}).get("summarize", {})
    return summarize.SummarizeService(
        api_key=summarize_config.get("chatgpt", {}).get("api_key"),
        system_template=summarize_config.get("query", {}).get("system_template"),
        user_template=summarize_config.get("query", {}).get("user_template"),
        query_str=summarize_config.get("query", {}).get("query_str"),
        content_format=summarize_config.get("query", {}).get("content_format", "plain"),
    )


def start_server(server: grpc.Server, config: CONFIG):
    try:
        server_config: CONFIG = config.get("server", {})
        address = f'{server_config.get("host", "localhost")}:{server_config.get("port", 50051)}'
        server.add_insecure_port(address=address)
        server.start()
        logger.info("Server started on %s", address)
        server.wait_for_termination()
    except Exception as e:
        logger.error("Error occurred while starting server: %s", e)
        raise


def serve(config: CONFIG):
    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=config.get("server", {}).get("max_workers", 10)
        )
    )

    search_service = create_search_service(config)
    search.add_SearchServiceServicer_to_server(search_service, server)
    logger.info("Added SearchService to server")

    summarize_service = create_summarize_service(config)
    summarize.add_SummarizeServiceServicer_to_server(summarize_service, server)
    logger.info("Added SummarizeService to server")

    start_server(server, config)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join("configs", "config.toml"),
        help="Path to the config file.",
    )
    return parser.parse_args()


def load_config(config_path):
    try:
        with open(config_path, "rb") as config_file:
            config = tomllib.load(config_file)
            return config
    except FileNotFoundError as e:
        logger.error("Config file not found: %s", e)
        raise
    except Exception as e:
        logger.error("Error loading config file: %s", e)
        raise


logger = logging.getLogger("server")


def main():
    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("server.log", "w"),
        ],
    )
    logger.setLevel(logging.INFO)

    args = parse_args()
    config = load_config(args.config)
    serve(config)
