"""Проверки порядка BFS, фильтра и циклов на тестовом графе."""

import unittest
from pathlib import Path

from src.graph import Package, build_graph
from src.local_repo import LocalRepository


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class GraphTests(unittest.TestCase):
    """Локальный граф с общим потомком, циклом и отдельным узлом."""

    def setUp(self):
        self.repo = LocalRepository(EXAMPLES / "graph.json")

    def graph(self, root="A", substring=""):
        """Построить граф от указанного пакета."""
        return build_graph(Package(root), self.repo.dependencies, substring)

    def test_bfs_keeps_back_edge(self):
        graph = self.graph()
        self.assertEqual([node.name for node in graph], list("ABCDE"))
        self.assertEqual(graph[Package("D")], (Package("B"),))

    def test_filter_skips_matching_packages(self):
        graph = self.graph(substring="b")
        self.assertEqual([node.name for node in graph], list("ACDE"))
        self.assertEqual(graph[Package("D")], ())

    def test_isolated_root(self):
        self.assertEqual(self.graph("F"), {Package("F"): ()})

    def test_unknown_root(self):
        with self.assertRaisesRegex(ValueError, "Z"):
            self.graph("Z")
