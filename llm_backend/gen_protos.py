import glob
import os
import subprocess


def generate():
    target_dir = os.path.join("llm_backend", "protos")
    proto_dir = os.path.join("protos")
    proto_files = glob.glob(f"{proto_dir}/*.proto")

    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"-I{target_dir}={proto_dir}",
        "--python_out=.",
        "--pyi_out=.",
        "--grpc_python_out=.",
    ] + proto_files

    subprocess.run(command, shell=False, check=True)
