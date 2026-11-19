"""Чтение и проверка настроек практической работы."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from packaging.version import InvalidVersion, Version


PACKAGE_NAME = re.compile(r"[A-Za-z0-9]+(?:[-_.]+[A-Za-z0-9]+)*")
TEST_NAME = re.compile(r"[A-Z]+")


@dataclass(frozen=True)
class Config:
    """Проверенные настройки; локальные пути привязаны к файлу JSON."""

    package: str
    repository: str | Path
    test_mode: bool
    version: str
    graph_image: Path
    ascii_tree: bool
    filter_substring: str


def read_object(path):
    """Прочитать объект JSON в кодировке UTF-8."""
    with path.open(encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: ожидается объект JSON")
    return data


def check_fields(data):
    """Проверить состав и типы всех семи параметров."""
    fields = {name: str for name in Config.__dataclass_fields__}
    fields.update(test_mode=bool, ascii_tree=bool)
    unknown = sorted(data.keys() - fields.keys())
    if unknown:
        raise ValueError(f"{unknown[0]}: неизвестный параметр")
    for name, field_type in fields.items():
        if name not in data:
            raise ValueError(f"{name}: обязательный параметр отсутствует")
        if not isinstance(data[name], field_type):
            raise ValueError(f"{name}: ожидается тип {field_type.__name__}")


def repository_location(value, test_mode, base):
    """Разрешить путь к тестовому графу или проверить URL API."""
    if test_mode:
        path = base / value
        if not value or not path.is_file():
            raise ValueError(f"repository: нет файла {path}")
        return path
    try:
        url = urlsplit(value)
        url.port
    except ValueError as exc:
        raise ValueError(f"repository: неверный URL ({exc})") from exc
    if (
        url.scheme not in {"http", "https"}
        or not url.hostname
        or url.username is not None
        or url.query
        or url.fragment
        or any(char.isspace() for char in value)
    ):
        raise ValueError("repository: нужен URL http(s) без учётных данных")
    return value.rstrip("/")


def load_config(path):
    """Проверить настройки CLI, возвращая имя ошибочного параметра."""
    data = read_object(path)
    check_fields(data)
    name_pattern = TEST_NAME if data["test_mode"] else PACKAGE_NAME
    if not name_pattern.fullmatch(data["package"]):
        raise ValueError("package: недопустимое имя пакета")
    try:
        Version(data["version"])
    except InvalidVersion as exc:
        raise ValueError("version: нужна версия по PEP 440") from exc
    image = Path(data["graph_image"])
    if image.suffix.lower() != ".png" or "\0" in str(image):
        raise ValueError("graph_image: нужен путь к файлу .png")
    data["graph_image"] = path.parent / image
    data["repository"] = repository_location(
        data["repository"], data["test_mode"], path.parent
    )
    return Config(**data)
