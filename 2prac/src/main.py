
"""Главный модуль Dependency Visualizer."""

from src.cli import parse_arguments, print_settings
from src.graph import (
    GraphBuilder,
    build_test_graph,
    get_load_order
)
from src.nuget import NuGetClient
from src.visualizer import generate_plantuml, generate_svg


def print_graph(graph):
    """Выводит вершины и связи графа."""

    print(f"\nВершин графа: {len(graph.vertices())}")

    for parent, child in sorted(graph.edges()):
        print(f"  {parent} -> {child}")


def build_test_mode_graph(settings):
    """Строит граф из тестового JSON-файла."""

    graph = build_test_graph(
        settings.test_file,
        settings.package,
        settings.depth,
        settings.filter_text
    )
    return graph, settings.package


def build_nuget_graph(settings):
    """Получает зависимости NuGet и строит граф."""

    client = NuGetClient(settings.repository)

    builder = GraphBuilder(
        client,
        settings.framework,
        settings.depth,
        settings.filter_text
    )

    dependencies = client.get_dependencies(
        settings.package,
        settings.version,
        settings.framework
    )

    print("\nПрямые зависимости:")

    for dependency in dependencies:
        print(
            f"  {dependency.package_id}: "
            f"{dependency.version_spec}"
        )

    graph = builder.build(
        settings.package,
        settings.version
    )

    root = f"{settings.package}@{settings.version}"
    return graph, root


def print_load_order(graph, root):
    """Выводит порядок загрузки пакетов."""

    print("\nПорядок загрузки:")

    for index, package in enumerate(
        get_load_order(graph, root),
        start=1
    ):
        print(f"{index}. {package}")


def generate_output_files(graph, settings):
    """Создаёт файлы PlantUML и SVG."""

    plantuml_file = generate_plantuml(
        graph,
        settings.output
    )

    svg_file = generate_svg(
        plantuml_file,
        settings.output,
        settings.plantuml
    )

    print(f"\nPlantUML: {plantuml_file}")
    print(f"SVG: {svg_file}")


def main():
    """Запускает полный процесс анализа зависимостей."""

    settings = parse_arguments()
    print_settings(settings)

    if settings.test_mode:
        graph, root = build_test_mode_graph(settings)
    else:
        graph, root = build_nuget_graph(settings)

    print_graph(graph)

    if settings.load_order:
        print_load_order(graph, root)

    generate_output_files(graph, settings)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1)
