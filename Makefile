PYTHON = poetry run python
PROTOC = $(PYTHON) -m grpc_tools.protoc

PROTO_DIR = ./protos
PROTO_FILES = $(wildcard $(PROTO_DIR)/*.proto)
TARGET_DIR = $(shell poetry version | cut -d' ' -f1 | sed 's/-/_/g')/grpc
TARGETS = $(patsubst $(PROTO_DIR)/%.proto,$(TARGET_DIR)/%_pb2.py,$(PROTO_FILES))

.PHONY: all serve clean

all: $(TARGETS)

serve: $(TARGETS)
	$(PYTHON) run_server.py --config configs/config.toml

$(TARGET_DIR)/%_pb2.py: $(PROTO_DIR)/%.proto
	@echo "Compiling $< to $(TARGET_DIR)..."
	$(PROTOC) \
		-I$(TARGET_DIR)=$(PROTO_DIR) \
		--python_out=. \
		--pyi_out=. \
		--grpc_python_out=. \
		$<
clean:
	rm -rf $(TARGET_DIR)
