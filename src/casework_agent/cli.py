import argparse
from pathlib import Path

import uvicorn

from .api import create_app
from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description='Local fictional casework agent')
    parser.add_argument('command', nargs='?', choices=['serve'], default='serve')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--port', type=int, default=8112, choices=[8112])
    args = parser.parse_args()
    uvicorn.run(create_app(Settings(root=args.root)), host='127.0.0.1', port=args.port, log_level='warning')


if __name__ == '__main__':
    main()
