"""Mermaid и консольное ASCII-дерево."""


def mermaid(graph):
    """Вернуть flowchart с устойчивыми идентификаторами узлов."""
    ids = {node: f"n{i}" for i, node in enumerate(graph)}
    lines = ["flowchart TD"]
    for node, node_id in ids.items():
        lines.append(f'    {node_id}["{node}"]')
    for source, children in graph.items():
        for target in children:
            lines.append(f"    {ids[source]} --> {ids[target]}")
    return "\n".join(lines) + "\n"


def ascii_tree(graph, root):
    """Печатать общие и циклические узлы без повторного раскрытия."""
    lines = [str(root)]
    seen = {root}
    stack = [(root, "", frozenset({root}), enumerate(graph[root], 1))]
    while stack:
        parent, prefix, ancestors, children = stack[-1]
        item = next(children, None)
        if item is None:
            stack.pop()
            continue
        index, child = item
        last = index == len(graph[parent])
        connector = "`-- " if last else "|-- "
        label = f"{prefix}{connector}{child}"
        if child in ancestors:
            lines.append(label + " (cycle)")
        elif child in seen:
            lines.append(label + " (shared)")
        else:
            lines.append(label)
            seen.add(child)
            indent = "    " if last else "|   "
            stack.append((
                child, prefix + indent, ancestors | {child},
                enumerate(graph[child], 1),
            ))
    return "\n".join(lines)
