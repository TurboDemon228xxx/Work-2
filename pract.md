# Проверка практической работы № 2

## Этап 4. Порядок установки

### Тестовый репозиторий

| Команда | Результат |
| --- | --- |
| `python -m src examples/test-cycle.json --order` | D, B, E, C, A. Программа сообщает о цикле D → B. |
| `python -m src examples/test-filter.json --order` | D, E, C, A. После исключения B цикла нет. |

### Сравнение с pip

Проверка выполнена на Windows, Python 3.12.14, pip 26.2.2. Использован
чистый каталог для установки, чтобы ранее установленные модули не
повлияли на вывод.

```powershell
python -m src examples/requests.json --order
python -m pip install --ignore-installed --only-binary=:all: --target out/pip-requests requests==2.32.3
```

| Инструмент | Порядок |
| --- | --- |
| CLI | charset-normalizer, idna, urllib3, certifi, requests |
| pip, строка `Installing collected packages` | urllib3, idna, charset-normalizer, certifi, requests |

Все четыре зависимости идут перед `requests`. Между этими четырьмя
пакетами нет рёбер, поэтому допустимы оба порядка. CLI обходит требования
в порядке записи в метаданных. pip устанавливает зависимости перед
зависящими пакетами и не гарантирует порядок независимых пакетов.
[Порядок установки в документации pip](https://pip.pypa.io/en/stable/cli/pip_install/#installation-order)
