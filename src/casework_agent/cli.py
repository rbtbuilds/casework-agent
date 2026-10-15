import argparse

import uvicorn

from .api import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Local fictional casework agent")
    parser.add_argument("command", choices=["serve"])
    parser.parse_args()
    uvicorn.run(create_app(),host="127.0.0.1",port=8112)
