"""Точка входа командной строки."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from .config import load_config


def main(argv=None):
    """Загрузить настройки и напечатать их в формате ключ=значение."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="путь к файлу JSON")
    args = parser.parse_args(argv)
    try:
        for key, value in asdict(load_config(args.config)).items():
            print(f"{key}={value}")
    except (OSError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
