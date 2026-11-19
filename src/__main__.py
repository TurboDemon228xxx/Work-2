"""Точка входа командной строки."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from packaging.utils import canonicalize_name

from .config import load_config
from .graph import Package, build_graph, graph_lines
from .local_repo import LocalRepository
from .order import installation_order
from .pypi import PyPIRepository
from .visual import ascii_tree, mermaid


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


def show_order(graph, root):
    """Показать порядок установки и сообщить о циклических рёбрах."""
    order, cycles = installation_order(graph, root)
    for source, target in cycles:
        print(f"Цикл: {source} -> {target}", file=sys.stderr)
    print("\n".join(map(str, order)))


def show_direct(repository, root, test_mode):
    """Показать требования PyPI или соседние узлы тестового пакета."""
    if test_mode:
        dependencies = repository.dependencies(root, lambda name: True)
    else:
        dependencies = repository.direct(root.name, root.version)
    print("\n".join(map(str, dependencies)) or "Прямых зависимостей нет.")


def render(graph, root, config):
    """Сохранить Mermaid и PNG, при необходимости вывести дерево."""
    from .png import save_png

    config.graph_image.parent.mkdir(parents=True, exist_ok=True)
    diagram_path = config.graph_image.with_suffix(".mmd")
    diagram_path.write_text(mermaid(graph), encoding="utf-8")
    save_png(graph, config.graph_image)
    print(f"Mermaid: {diagram_path}")
    print(f"PNG: {config.graph_image}")
    if config.ascii_tree:
        print(ascii_tree(graph, root))


def analyze(config, args):
    """Выполнить выбранную операцию над зависимостями."""
    repository, root = open_repository(config)
    if args.direct:
        show_direct(repository, root, config.test_mode)
        return
    graph = build_graph(root, repository.dependencies, config.filter_substring)
    if args.order:
        show_order(graph, root)
    elif args.graph:
        print("\n".join(graph_lines(graph)))
    else:
        render(graph, root, config)


def main(argv=None):
    """Загрузить настройки и выполнить выбранную операцию."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="путь к файлу JSON")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--show-config", action="store_true",
                       help="проверить и вывести конфигурацию")
    modes.add_argument("--direct", action="store_true",
                       help="показать прямые зависимости")
    modes.add_argument("--graph", action="store_true",
                       help="показать список смежности в порядке BFS")
    modes.add_argument("--order", action="store_true",
                       help="показать порядок установки")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.show_config:
            show_config(config)
        else:
            analyze(config, args)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
