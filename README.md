# SYNC Server LLM

## Installation

```shell
git clone --recurse-submodules https://github.com/NCTU-SYNC/sync-server-llm.git
cd sync-server-llm

uv run gen-protos
```

## Usage

Please setup the configuration file `configs/config.toml` before running the server.
You can refer to the `configs/example.toml` for the format.

```shell
uv run serve --config configs/config.toml
```

## Features

Please refer to the protobuf files in `protos/` for the features provided by the server.
