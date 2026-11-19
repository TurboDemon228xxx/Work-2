"""Порядок установки: зависимости перед зависящими пакетами."""


def installation_order(graph, root):
    """Вернуть постпорядок DFS и обратные рёбра, мешающие сортировке."""
    ordered = []
    cycles = []
    active = {root}
    completed = set()
    stack = [(root, iter(graph[root]))]
    while stack:
        package, children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            active.remove(package)
            completed.add(package)
            ordered.append(package)
        elif child in active:
            cycles.append((package, child))
        elif child not in completed:
            active.add(child)
            stack.append((child, iter(graph[child])))
    return ordered, cycles
