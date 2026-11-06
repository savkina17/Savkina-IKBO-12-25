
"""Тесты построения графа зависимостей."""

from src.graph import (
    DependencyGraph,
    GraphBuilder,
    build_test_graph,
    get_load_order
)
from src.nuget import Dependency


class FakeClient:
    """Имитирует NuGet-клиент без HTTP-запросов."""

    def __init__(self):
        """Создаёт заранее заданные зависимости."""

        self.data = {
            "A": [Dependency("B", "1.0"), Dependency("C", "1.0")],
            "B": [Dependency("D", "1.0")],
            "C": [Dependency("D", "1.0")],
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

    builder = GraphBuilder(FakeClient(), "net8.0", 5, "")
    graph = builder.build("A", "1.0")

    assert len(graph.vertices()) == 4
    assert ("B@1.0", "D@1.0") in graph.edges()


def test_depth_limit():
    """Проверяет ограничение глубины обхода."""

    builder = GraphBuilder(FakeClient(), "net8.0", 1, "")
    graph = builder.build("A", "1.0")

    assert len(graph.vertices()) == 3
    assert not any(
        parent.startswith("B@") for parent, child in graph.edges()
    )


def test_filter():
    """Проверяет исключение пакетов по подстроке."""

    builder = GraphBuilder(FakeClient(), "net8.0", 5, "C")
    graph = builder.build("A", "1.0")

    assert "C@1.0" not in graph.vertices()


def test_cycle_detection_in_bfs():
    """Проверяет безопасный обход циклического графа."""

    client = FakeClient()
    client.data["D"] = [Dependency("A", "1.0")]

    builder = GraphBuilder(client, "net8.0", 5, "")
    graph = builder.build("A", "1.0")

    assert len(graph.vertices()) == 4


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

    graph = build_test_graph(path, "A", 1, "")

    assert "B" in graph.vertices()
    assert "C" not in graph.vertices()