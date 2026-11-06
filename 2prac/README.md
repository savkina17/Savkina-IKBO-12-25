
# Dependency Visualizer

Инструмент для анализа и визуализации графа зависимостей
пакетов NuGet.

## 1. Описание

Программа получает информацию о зависимостях NuGet-пакетов
через HTTP-запросы к NuGet-репозиторию.

Полученные данные анализируются собственным алгоритмом
рекурсивного BFS.

Результатом работы является граф зависимостей,
представленный в формате PlantUML и SVG.

Готовые менеджеры пакетов и библиотеки для получения
зависимостей внутри анализатора не используются.

## 2. Возможности

- Получение метаданных NuGet-пакетов.
- Извлечение прямых зависимостей из nuspec.
- Построение транзитивного графа.
- Рекурсивный алгоритм BFS.
- Ограничение глубины анализа.
- Фильтрация пакетов по подстроке.
- Обнаружение циклических зависимостей.
- Тестовый режим с JSON-репозиторием.
- Вычисление порядка загрузки.
- Генерация PlantUML.
- Создание SVG-диаграмм.

## 3. Требованисвя

- Python 3.11 или новее.
- Java для запуска PlantUML.
- Установленный PlantUML CLI.

Основная программа использует стандартную библиотеку Python.

## 4. Запуск

Клонирование репозитория:

```bash
git clone <repository-url>
cd dependency-visualizer
```

Запуск:

```bash
python -m src.main \
  --package Newtonsoft.Json \
  --version 13.0.3
```

В Windows также можно использовать:

```powershell
run.bat --package Newtonsoft.Json --version 13.0.3
```

## 5. Параметры

| Параметр | Описание |
|---|---|
| --package | Имя пакета |
| --version | Версия пакета |
| --repository | URL NuGet-репозитория |
| --output | Имя SVG-файла |
| --depth | Максимальная глубина |
| --filter | Подстрока исключаемых пакетов |
| --test-mode | Включение тестового режима |
| --test-file | Путь к JSON-графу |
| --load-order | Вывод порядка загрузки |
| --framework | Целевая платформа .NET |
| --plantuml | Команда запуска PlantUML |

## 6. Примеры

Обычный анализ:

```bash
python -m src.main \
  --package Newtonsoft.Json \
  --version 13.0.3 \
  --depth 3
```

С фильтрацией:

```bash
python -m src.main \
  --package Newtonsoft.Json \
  --version 13.0.3 \
  --filter Microsoft
```

С порядком загрузки:

```bash
python -m src.main \
  --package Newtonsoft.Json \
  --version 13.0.3 \
  --load-order
```

Тестовый режим:

```bash
python -m src.main \
  --package A \
  --test-mode \
  --test-file test_repository/graph.json \
  --depth 3
```

## 7. Результаты

Программа создаёт:

- файл `.puml` с текстовым представлением графа;
- файл `.svg` с изображением графа.

Результаты сохраняются в папке output.

## 8. Тестирование

Установка pytest:

```bash
python -m pip install pytest
```

Запуск тестов:

```bash
python -m pytest tests -v
```

## 9. Проверка качества кода

```bash
python -m pip install ruff radon coverage
```

Проверка PEP8:

```bash
ruff check src tests
```

Проверка сложности:

```bash
radon cc src -s -a
```

Проверка покрытия:

```bash
coverage run -m pytest
coverage report
```

## 10. Ограничения

Выбор зависимостей NuGet зависит от целевой платформы.
При отсутствии точного совпадения framework-группы
используется резервный вариант.

Поддержка сложных NuGet-правил разрешения версий
и совместимости платформ требует отдельной проверки.