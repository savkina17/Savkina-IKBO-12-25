
"""Тесты построения графа зависимостей."""

from src.graph import (
    DependencyGraph,
    GraphBuilder,
    build_test_graph,
    get_load_order
)
from src.nuget import Dependency


# Константы тестовых данных
PACKAGE_VERSION = "1.0"
FRAMEWORK = "net8.0"
DEFAULT_FILTER = ""
DEFAULT_DEPTH = 5
LIMITED_DEPTH = 1

EXPECTED_GRAPH_SIZE = 4
EXPECTED_LIMITED_GRAPH_SIZE = 3

ROOT_PACKAGE = "A"
DEPENDENCY_PACKAGE = "B"
TRANSITIVE_PACKAGE = "D"


class FakeClient:
    """Имитирует NuGet-клиент без HTTP-запросов."""

    def __init__(self):
        """Создаёт заранее заданные зависимости."""

        self.data = {
            "A": [
                Dependency("B", PACKAGE_VERSION),
                Dependency("C", PACKAGE_VERSION)
            ],
            "B": [Dependency("D", PACKAGE_VERSION)],
            "C": [Dependency("D", PACKAGE_VERSION)],
            "D": []
        }

    def get_dependencies(self, package_id, version, framework):
        """Возвращает зависимости указанного пакета."""

        return self.data.get(package_id, [])

    def resolve_version(self, package_id, specification):
        """Возвращает фиксированную версию."""

        return specification


def test_graph_edges():
    """Проверяет добавление вершин и рёбер."""

    graph = DependencyGraph()
    graph.add_edge("A", "B")

    assert "A" in graph.vertices()
    assert ("A", "B") in graph.edges()


def test_recursive_bfs():
    """Проверяет транзитивное построение графа."""

    builder = GraphBuilder(
        FakeClient(), FRAMEWORK, DEFAULT_DEPTH, DEFAULT_FILTER
    )
    graph = builder.build(ROOT_PACKAGE, PACKAGE_VERSION)

    assert len(graph.vertices()) == EXPECTED_GRAPH_SIZE
    assert (
        f"{DEPENDENCY_PACKAGE}@{PACKAGE_VERSION}",
        f"{TRANSITIVE_PACKAGE}@{PACKAGE_VERSION}"
    ) in graph.edges()


def test_depth_limit():
    """Проверяет ограничение глубины обхода."""

    builder = GraphBuilder(
        FakeClient(), FRAMEWORK, LIMITED_DEPTH, DEFAULT_FILTER
    )
    graph = builder.build(ROOT_PACKAGE, PACKAGE_VERSION)

    assert len(graph.vertices()) == EXPECTED_LIMITED_GRAPH_SIZE
    assert not any(
        parent.startswith(f"{DEPENDENCY_PACKAGE}@")
        for parent, child in graph.edges()
    )


def test_filter():
    """Проверяет исключение пакетов по подстроке."""

    builder = GraphBuilder(
        FakeClient(), FRAMEWORK, DEFAULT_DEPTH, "C"
    )
    graph = builder.build(ROOT_PACKAGE, PACKAGE_VERSION)

    assert f"C@{PACKAGE_VERSION}" not in graph.vertices()


def test_cycle_detection_in_bfs():
    """Проверяет безопасный обход циклического графа."""

    client = FakeClient()
    client.data["D"] = [Dependency("A", PACKAGE_VERSION)]

    builder = GraphBuilder(
        client, FRAMEWORK, DEFAULT_DEPTH, DEFAULT_FILTER
    )
    graph = builder.build(ROOT_PACKAGE, PACKAGE_VERSION)

    assert len(graph.vertices()) == EXPECTED_GRAPH_SIZE


def test_load_order():
    """Проверяет порядок загрузки зависимостей."""

    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")

    order = get_load_order(graph, "A")

    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")


def test_load_order_cycle():
    """Проверяет обнаружение цикла при сортировке."""

    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")

    try:
        get_load_order(graph, "A")
        assert False, "Expected cycle error"
    except ValueError:
        assert True


def test_test_repository(tmp_path):
    """Проверяет чтение и построение тестового графа."""

    path = tmp_path / "graph.json"
    path.write_text(
        '{"A":["B"],"B":["C"],"C":[]}',
        encoding="utf-8"
    )

    graph = build_test_graph(
        path, ROOT_PACKAGE, LIMITED_DEPTH, DEFAULT_FILTER
    )

    assert "B" in graph.vertices()
    assert "C" not in graph.vertices()
