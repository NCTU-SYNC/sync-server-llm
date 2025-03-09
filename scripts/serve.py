import argparse
import asyncio
import logging
import os
import tomllib
from concurrent import futures

import grpc

from llm_backend import Config, setup_search_service, setup_summarize_service


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


async def serve(config: Config, logger: logging.Logger):
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=config.server.max_workers)
    )
    setup_search_service(config, server)
    logger.info("Added SearchService to server")

    setup_summarize_service(config, server)
    logger.info("Added SummarizeService to server")

    server_config = config.server
    address = f"{server_config.host}:{server_config.port}"
    server.add_insecure_port(address=address)
    logger.info("Server started on %s", address)

    await server.start()

    async def server_graceful_shutdown():
        logging.info("Starting graceful shutdown...")
        await server.stop(3)

    _cleanup_coroutines.append(server_graceful_shutdown())

    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s\t%(levelname)s: %(message)s")
    logger = logging.getLogger("server")
    logger.setLevel(logging.INFO)

    args = parse_args()
    config = load_config(args.config)

    loop = asyncio.new_event_loop()
    _cleanup_coroutines = []
    try:
        loop.run_until_complete(serve(config, logger))
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
