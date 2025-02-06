import argparse
import logging
import os
import sys
import tomllib
from concurrent import futures

import grpc

from llm_backend import Config, setup_search_service, setup_summarize_service


def start_server(server: grpc.Server, config: Config):
    try:
        server_config = config.server
        address = f"{server_config.host}:{server_config.port}"
        server.add_insecure_port(address=address)
        server.start()
        logger.info("Server started on %s", address)
        server.wait_for_termination()
    except Exception as e:
        logger.error("Error occurred while starting server: %s", e)
        raise


def serve(config: Config):
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.server.max_workers)
    )

    setup_search_service(config, server)
    logger.info("Added SearchService to server")

    setup_summarize_service(config, server)
    logger.info("Added SummarizeService to server")

    start_server(server, config)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join("configs", "example.toml"),
        help="Path to the config file.",
    )
    return parser.parse_args()


def load_config(config_path):
    try:
        with open(config_path, "rb") as config_file:
            config = tomllib.load(config_file)
    except FileNotFoundError as e:
        logger.error("Config file not found: %s", e)
        raise
    return Config.model_validate(config)


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
