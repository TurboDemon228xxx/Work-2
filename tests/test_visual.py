"""Проверки Mermaid, ASCII и сохранения настоящего PNG."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.graph import Package
from src.png import graph_columns, save_png
from src.visual import ascii_tree, mermaid


class VisualTests(unittest.TestCase):
    """Небольшой граф с циклом, общим узлом и листом."""

    def setUp(self):
        a, b, c, d = map(Package, "ABCD")
        self.root = a
        self.graph = {a: (b, c), b: (d,), c: (d,), d: (a,)}

    def test_ascii_tree(self):
        text = ascii_tree(self.graph, self.root)
        self.assertIn("A (cycle)", text)
        self.assertIn("D (shared)", text)
        self.assertTrue(text.isascii())

    def test_mermaid_keeps_cycle(self):
        text = mermaid(self.graph)
        self.assertTrue(text.startswith("flowchart TD\n"))
        self.assertIn('n0["A"]', text)
        self.assertIn("n3 --> n0", text)

    def test_png_can_be_opened(self):
        sizes = [len(column) for column in graph_columns(self.graph)]
        self.assertEqual(sizes, [1, 2, 1])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.png"
            save_png(self.graph, path)
            with Image.open(path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertGreater(image.width, image.height)
                image.verify()
