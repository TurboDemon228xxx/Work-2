# Практическая работа № 2 · Вариант 26

CLI для анализа зависимостей Python-пакетов. Настройки хранятся в JSON.
Прямые зависимости выбранного выпуска читаются из поля requires_dist
ответа PyPI JSON API. HTTP-запрос выполняет urllib из стандартной
библиотеки. Маркеры требований проверяются для текущего Python.

## Запуск

    python -m pip install -r requirements.txt
    python -m src examples/requests.json --show-config
    python -m src examples/requests.json
    python -m unittest discover -s tests -v
