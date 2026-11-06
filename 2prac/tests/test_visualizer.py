
"""Тесты генерации PlantUML."""

from src.graph import DependencyGraph
from src.visualizer import generate_plantuml


def test_plantuml_generation(tmp_path):
    """Проверяет формирование текста диаграммы."""

    graph = DependencyGraph()
    graph.add_edge("Package.A", "Package.B")

    path = generate_plantuml(
        graph,
        str(tmp_path / "result.svg")
    )

    content = path.read_text(encoding="utf-8")

    assert "@startuml" in content
    assert "@enduml" in content
    assert "-->" in content
    assert "Package.A" in content
    assert "Package.B" in content