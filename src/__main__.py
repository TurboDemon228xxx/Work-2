"""Точка входа командной строки."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from packaging.utils import canonicalize_name

from .config import load_config
from .graph import Package, build_graph, graph_lines
from .local_repo import LocalRepository
from .pypi import PyPIRepository


def show_config(config):
    """Вывести проверенные параметры из первого этапа."""
    for key, value in asdict(config).items():
        print(f"{key}={value}")


def open_repository(config):
    """Подготовить загрузчик зависимостей и начальный узел."""
    if config.test_mode:
        return LocalRepository(config.repository), Package(config.package)
    root = Package(canonicalize_name(config.package), config.version)
    return PyPIRepository(config.repository), root


def analyze(config, direct_only):
    """Напечатать прямые зависимости либо полный список смежности."""
    repository, root = open_repository(config)
    if direct_only and not config.test_mode:
        direct = repository.direct(root.name, root.version)
        print("\n".join(map(str, direct)) or "Прямых зависимостей нет.")
        return
    if direct_only:
        direct = repository.dependencies(root, lambda name: True)
        print("\n".join(map(str, direct)) or "Прямых зависимостей нет.")
        return
    graph = build_graph(root, repository.dependencies, config.filter_substring)
    print("\n".join(graph_lines(graph)))


def main(argv=None):
    """Загрузить настройки и выполнить выбранную операцию."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="путь к файлу JSON")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--show-config", action="store_true")
    modes.add_argument("--direct", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.show_config:
            show_config(config)
        else:
            analyze(config, args.direct)
    except (OSError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
