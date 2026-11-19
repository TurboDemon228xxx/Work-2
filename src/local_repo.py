"""Тестовый репозиторий с графом, заданным объектом JSON."""

from .config import TEST_NAME, read_object
from .graph import Package


class LocalRepository:
    """Читает списки смежности для пакетов A, B, AA и т. д."""

    def __init__(self, path):
        self.entries = read_object(path)
        for name, children in self.entries.items():
            if not TEST_NAME.fullmatch(name):
                raise ValueError(f"{name}: имя должно содержать A–Z")
            if not isinstance(children, list):
                raise ValueError(f"{name}: ожидается список зависимостей")
            for child in children:
                if not isinstance(child, str) or child not in self.entries:
                    raise ValueError(f"{name}: неизвестная зависимость {child}")

    def dependencies(self, package, allowed):
        """Вернуть доступные соседние узлы и проверить наличие пакета."""
        if package.name not in self.entries:
            raise ValueError(f"{package.name}: пакета нет в тестовом графе")
        return [
            Package(name) for name in self.entries[package.name]
            if allowed(name)
        ]
