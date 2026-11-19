"""Проверка загрузки JSON и ошибок всех параметров."""

import json
import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID = {
    "package": "requests",
    "repository": "https://pypi.org",
    "test_mode": False,
    "version": "2.32.3",
    "graph_image": "out/graph.png",
    "ascii_tree": False,
    "filter_substring": "",
}


class ConfigTests(unittest.TestCase):
    """Проверки настроек без обращения к сети."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "config.json"

    def load(self, **changes):
        """Записать параметры примера с заданными заменами."""
        self.path.write_text(json.dumps(VALID | changes), encoding="utf-8")
        return load_config(self.path)

    def test_valid(self):
        config = self.load()
        self.assertEqual(config.package, "requests")
        self.assertEqual(config.graph_image, self.path.parent / "out/graph.png")

    def test_each_invalid_parameter(self):
        cases = {
            "package": "../requests",
            "repository": "file:///repo",
            "test_mode": "no",
            "version": "latest",
            "graph_image": "graph.jpg",
            "ascii_tree": 1,
            "filter_substring": None,
        }
        for name, value in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(
                ValueError, name
            ):
                self.load(**{name: value})

    def test_missing_fixture(self):
        with self.assertRaisesRegex(ValueError, "repository"):
            self.load(test_mode=True, package="A", repository="absent.json")

    def test_local_path_relative_to_config(self):
        graph = self.path.parent / "repo.json"
        graph.write_text("{}", encoding="utf-8")
        config = self.load(test_mode=True, package="AA", repository=graph.name)
        self.assertEqual(config.repository, graph)
