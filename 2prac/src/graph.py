
"""Построение и обработка графа зависимостей."""

import json
from collections import deque
from pathlib import Path


class DependencyGraph:
    """Хранит граф зависимостей в виде списка смежности."""

    def __init__(self):
        """Создаёт пустой граф."""

        self.adjacency = {}

    def add_vertex(self, vertex):
        """Добавляет вершину, если её ещё нет."""

        self.adjacency.setdefault(vertex, set())

    def add_edge(self, parent, child):
        """Добавляет направленное ребро зависимости."""

        self.add_vertex(parent)
        self.add_vertex(child)
        self.adjacency[parent].add(child)

    def vertices(self):
        """Возвращает все вершины графа."""

        return set(self.adjacency)

    def edges(self):
        """Возвращает все рёбра графа."""

        return [
            (parent, child)
            for parent, children in self.adjacency.items()
            for child in children
        ]


class GraphBuilder:
    """Строит граф с помощью рекурсивного BFS."""

    def __init__(self, client, framework, max_depth, filter_text):
        """Сохраняет параметры построения графа."""

        self.client = client
        self.framework = framework
        self.max_depth = max_depth
        self.filter_text = filter_text.lower()
        self.graph = DependencyGraph()
        self.visited = set()

    def is_filtered(self, package_id):
        """Проверяет, нужно ли исключить пакет."""

        return bool(
            self.filter_text
            and self.filter_text in package_id.lower()
        )

    def build(self, package_id, version):
        """Запускает обход от корневого пакета."""

        root = f"{package_id}@{version}"
        queue = deque([(package_id, version, root, 0)])

        self.graph.add_vertex(root)
        self.visited.add(root)
        self.bfs(queue)

        return self.graph

    def bfs(self, queue):
        """Рекурсивно обходит граф в ширину."""

        if not queue:
            return

        package_id, version, parent, depth = queue.popleft()
        print(f"Исследуем: {parent}")

        if depth < self.max_depth:
            dependencies = self.client.get_dependencies(
                package_id, version, self.framework
            )

            for dependency in dependencies:
                if self.is_filtered(dependency.package_id):
                    continue

                child_version = self.client.resolve_version(
                    dependency.package_id,
                    dependency.version_spec
                )

                child = f"{dependency.package_id}@{child_version}"
                self.graph.add_edge(parent, child)

                if child not in self.visited:
                    self.visited.add(child)
                    queue.append(
                        (
                            dependency.package_id,
                            child_version,
                            child,
                            depth + 1
                        )
                    )

        self.bfs(queue)


def load_test_graph(file_path):
    """Загружает тестовый граф из JSON-файла."""

    path = Path(file_path)
    return json.loads(path.read_text(encoding="utf-8"))


def build_test_graph(file_path, root, max_depth, filter_text):
    """Строит ограниченный по глубине тестовый граф."""

    data = load_test_graph(file_path)
    graph = DependencyGraph()
    visited = {root}
    queue = deque([(root, 0)])
    filter_value = filter_text.lower()

    graph.add_vertex(root)

    def bfs():
        """Рекурсивно обходит тестовый граф."""

        if not queue:
            return

        vertex, depth = queue.popleft()

        if depth < max_depth:
            children = data.get(vertex, [])

            for child in children:
                if filter_value and filter_value in child.lower():
                    continue

                graph.add_edge(vertex, child)

                if child not in visited:
                    visited.add(child)
                    queue.append((child, depth + 1))

        bfs()

    bfs()
    return graph


def get_load_order(graph, root):
    """Возвращает порядок загрузки через топологическую сортировку."""

    visited = set()
    temporary = set()
    result = []

    def visit(vertex):
        """Рекурсивно посещает зависимости перед родителем."""

        if vertex in temporary:
            raise ValueError("Обнаружен цикл зависимостей")

        if vertex in visited:
            return

        temporary.add(vertex)

        for child in sorted(graph.adjacency.get(vertex, set())):
            visit(child)

        temporary.remove(vertex)
        visited.add(vertex)
        result.append(vertex)

    visit(root)
    return result