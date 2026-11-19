"""Граф и рекурсивный обход в ширину по уровням."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    """Узел графа с версией и активными дополнительными группами."""

    name: str
    version: str = ""
    extras: tuple[str, ...] = ()

    def __str__(self):
        extras = f"[{','.join(self.extras)}]" if self.extras else ""
        version = f"=={self.version}" if self.version else ""
        return f"{self.name}{extras}{version}"


def build_graph(root, dependencies, filter_substring=""):
    """Добавлять узлы по слоям BFS, сохраняя обратные рёбра циклов."""
    graph = {}
    seen = {root}
    needle = filter_substring.casefold()

    def allowed(name):
        """Проверить имя зависимости перед обработкой ребра."""
        return not needle or needle not in name.casefold()

    def visit_level(level):
        """Обработать уровень и рекурсивно перейти к следующему."""
        following = []
        for package in level:
            children = tuple(dict.fromkeys(dependencies(package, allowed)))
            graph[package] = children
            for child in children:
                if child not in seen:
                    seen.add(child)
                    following.append(child)
        if following:
            visit_level(following)

    visit_level([root])
    return graph


def graph_lines(graph):
    """Описать список смежности в порядке обхода."""
    for package, children in graph.items():
        yield f"{package} -> {', '.join(map(str, children)) or '-'}"
