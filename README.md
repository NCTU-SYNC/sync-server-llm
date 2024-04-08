# SYNC Server LLM

## Installation

```shell
git clone --recurse-submodules https://github.com/NCTU-SYNC/sync-server-llm.git
cd sync-server-llm

poetry install
make
```

## Usage

Please setup the configuration file `configs/config.toml` before running the server.
You can refer to the `configs/example.toml` for the format.

```shell
make serve
```

## Features

1. [Semantic Search](https://github.com/NCTU-SYNC/llm-microservice-protos/blob/282d4dc1f7d8b1a96508fc43cef4fe10fde0d301/search.proto)
2. [Summarization](https://github.com/NCTU-SYNC/llm-microservice-protos/blob/282d4dc1f7d8b1a96508fc43cef4fe10fde0d301/summarize.proto)
