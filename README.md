# Практическая работа № 2 · Вариант 26

CLI для анализа зависимостей Python-пакетов. Настройки хранятся в JSON.
Прямые зависимости выбранного выпуска читаются из поля requires_dist
ответа PyPI JSON API. HTTP-запрос выполняет urllib из стандартной
библиотеки. Маркеры требований проверяются для текущего Python.

## Запуск

    python -m pip install -r requirements.txt
    python -m src examples/requests.json --show-config
    python -m src examples/requests.json --direct
    python -m src examples/test-cycle.json
    python -m src examples/test-filter.json
    python -m src examples/test-cycle.json --order
    python -m src examples/test-filter.json --order
    python -m unittest discover -s tests -v

Граф строится рекурсивным BFS по уровням. Первый тестовый конфиг содержит
цикл B → D → B и общую зависимость D. Второй исключает B по подстроке.

Режим --order выводит порядок установки зависимостей, затем корневой
пакет. В ациклическом графе каждая зависимость располагается раньше
своего потребителя. При цикле программа показывает ребро цикла в
стандартном потоке ошибок и печатает порядок обхода остальных рёбер.
