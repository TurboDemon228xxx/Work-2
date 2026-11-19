"""Получение метаданных выпусков через публичный JSON API PyPI."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


REQUEST_TIMEOUT = 15


class PyPIRepository:
    """Читает requires_dist напрямую через HTTP и кэширует ответы."""

    def __init__(self, base_url):
        self.base_url = base_url
        self.cache = {}

    def fetch(self, name, version=""):
        """Получить один выпуск либо ответ со списком выпусков проекта."""
        path = "/".join(quote(part, safe="") for part in (name, version) if part)
        if path not in self.cache:
            url = f"{self.base_url}/pypi/{path}/json"
            self.cache[path] = download_json(url)
        return self.cache[path]

    def direct(self, name, version, extras=()):
        """Вернуть активные требования указанного выпуска."""
        data = self.fetch(canonicalize_name(name), version)
        info = data.get("info")
        if not isinstance(info, dict):
            raise ValueError(f"{name}=={version}: нет объекта info")
        declarations = info.get("requires_dist")
        if declarations is None:
            return []
        if not isinstance(declarations, list) or not all(
            isinstance(item, str) for item in declarations
        ):
            raise ValueError(f"{name}=={version}: неверный requires_dist")
        return active_requirements(declarations, extras)


def download_json(url):
    """Декодировать HTTP-ответ и добавить адрес в сообщение об ошибке."""
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise ValueError(f"{url}: HTTP {exc.code} {exc.reason}") from exc
    except (URLError, TimeoutError, ValueError) as exc:
        raise ValueError(f"{url}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{url}: ожидается объект JSON")
    return data


def active_requirements(declarations, extras):
    """Применить PEP 508-маркеры для текущего Python и активных extras."""
    requirements = [Requirement(declaration) for declaration in declarations]
    contexts = ("", *extras)
    return [
        req for req in requirements
        if req.marker is None or any(
            req.marker.evaluate({"extra": extra}) for extra in contexts
        )
    ]
