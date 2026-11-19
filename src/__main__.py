"""Точка входа командной строки."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from .config import load_config
from .pypi import PyPIRepository


def show_config(config):
    """Вывести проверенные параметры из первого этапа."""
    for key, value in asdict(config).items():
        print(f"{key}={value}")


def main(argv=None):
    """Загрузить настройки и вывести прямые зависимости из PyPI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="путь к файлу JSON")
    parser.add_argument("--show-config", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.show_config:
            show_config(config)
        elif config.test_mode:
            raise ValueError("тестовый репозиторий появится на этапе 3")
        else:
            repository = PyPIRepository(config.repository)
            direct = repository.direct(config.package, config.version)
            print("\n".join(map(str, direct)) or "Прямых зависимостей нет.")
    except (OSError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
