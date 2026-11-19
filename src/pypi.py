"""Получение метаданных выпусков через публичный JSON API PyPI."""

import json
import platform
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

from .graph import Package


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

    def dependencies(self, package, allowed):
        """Разрешить активные зависимости выбранного узла."""
        requirements = self.direct(package.name, package.version, package.extras)
        result = []
        for req in requirements:
            name = canonicalize_name(req.name)
            if allowed(name):
                result.append(self.resolve(name, req))
        return result

    def resolve(self, name, requirement):
        """Выбрать наиболее свежую версию для одного требования."""
        if requirement.url:
            raise ValueError(f"{name}: прямые URL в требованиях не поддержаны")
        releases = self.fetch(name).get("releases")
        if not isinstance(releases, dict):
            raise ValueError(f"{name}: ответ API не содержит список releases")
        options = compatible_releases(releases)
        matches = requirement.specifier.filter(options, prereleases=None)
        chosen = max(matches, default=None)
        if chosen is None:
            raise ValueError(f"{name}{requirement.specifier}: нет версии")
        extras = tuple(sorted(map(canonicalize_name, requirement.extras)))
        return Package(name, options[chosen], extras)


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


def compatible_releases(releases):
    """Оставить выпуски с файлами для текущей версии Python."""
    python = Version(platform.python_version())
    result = {}
    for release, files in releases.items():
        try:
            version = Version(release)
        except InvalidVersion:
            continue
        if files and any(file_supports_python(file, python) for file in files):
            result[version] = release
    return result


def file_supports_python(file, python):
    """Проверить признак yanked и ограничение Requires-Python."""
    if file.get("yanked"):
        return False
    specifier = file.get("requires_python")
    return not specifier or SpecifierSet(specifier).contains(python)
