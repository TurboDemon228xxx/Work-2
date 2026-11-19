"""Проверки чтения метаданных и отбора прямых зависимостей."""

import unittest
from unittest.mock import patch

from packaging.requirements import Requirement

from src.graph import Package
from src.pypi import PyPIRepository


class PyPITests(unittest.TestCase):
    """Подменяет HTTP-ответы для работы без сети."""

    @patch("src.pypi.download_json")
    def test_pinned_release_and_markers(self, download):
        download.return_value = {"info": {"requires_dist": [
            "certifi>=2024",
            'pytest; extra == "test"',
            'typing-extensions; python_version < "3.0"',
        ]}}
        repo = PyPIRepository("https://example.org")
        self.assertEqual(
            [str(req) for req in repo.direct("My_Package", "1.2.0")],
            ["certifi>=2024"],
        )
        self.assertEqual(
            [req.name for req in repo.direct("my-package", "1.2.0", ("test",))],
            ["certifi", "pytest"],
        )
        download.assert_called_once_with(
            "https://example.org/pypi/my-package/1.2.0/json"
        )

    @patch("src.pypi.download_json", return_value={"info": {}})
    def test_no_dependencies(self, _download):
        repo = PyPIRepository("https://example.org")
        self.assertEqual(repo.direct("leaf", "1.0"), [])

    @patch("src.pypi.download_json")
    def test_resolves_latest_compatible_release(self, download):
        download.return_value = {"releases": {
            "1.0": [{}],
            "1.5": [{"requires_python": ">=3.10"}],
            "1.6": [{"yanked": True}],
            "1.7": [{"requires_python": ">=99"}],
            "2.0": [{}],
        }}
        repo = PyPIRepository("https://example.org")
        req = Requirement("leaf[foo]>=1,<2")
        expected = Package("leaf", "1.5", ("foo",))
        self.assertEqual(repo.resolve("leaf", req), expected)
