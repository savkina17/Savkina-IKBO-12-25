
"""Формирование PlantUML и генерация SVG."""

import subprocess
from pathlib import Path


def create_identifiers(vertices):
    """Создаёт идентификаторы для вершин графа."""

    return {
        vertex: f"N{index}"
        for index, vertex in enumerate(sorted(vertices))
    }


def add_vertices(lines, vertices, identifiers):
    """Добавляет вершины графа в диаграмму."""

    for vertex in vertices:
        label = vertex.replace('"', "'")
        lines.append(
            f'object "{label}" as {identifiers[vertex]}'
        )


def add_edges(lines, edges, identifiers):
    """Добавляет связи между вершинами графа."""

    for parent, child in sorted(edges):
        source = identifiers[parent]
        target = identifiers[child]
        lines.append(f"{source} --> {target}")


def save_plantuml(lines, output_file):
    """Сохраняет текст диаграммы в файл PlantUML."""

    path = Path(output_file).with_suffix(".puml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return path


def generate_plantuml(graph, output_file):
    """Преобразует граф в текстовую диаграмму PlantUML."""

    vertices = sorted(graph.vertices())
    identifiers = create_identifiers(vertices)

    lines = ["@startuml", "left to right direction"]

    add_vertices(lines, vertices, identifiers)
    add_edges(lines, graph.edges(), identifiers)

    lines.append("@enduml")

    return save_plantuml(lines, output_file)


def build_plantuml_command(command, plantuml_file, output_dir):
    """Формирует команду запуска PlantUML."""

    if command.lower().endswith(".jar"):
        executable = ["java", "-jar", command]
    else:
        executable = [command]

    return executable + [
        "-tsvg",
        str(plantuml_file.resolve()),
        "-o",
        str(output_dir.resolve())
    ]


def run_plantuml(command):
    """Запускает PlantUML и проверяет результат выполнения."""

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"PlantUML error: {result.stderr}"
        )


def move_generated_svg(plantuml_file, output):
    """Перемещает SVG в заданный путь и проверяет его наличие."""

    generated = output.parent / (
        plantuml_file.stem + ".svg"
    )

    if generated != output and generated.exists():
        generated.replace(output)

    if not output.is_file():
        raise RuntimeError("SVG file was not generated")


def generate_svg(plantuml_file, output_file, command):
    """Запускает PlantUML и сохраняет SVG."""

    output = Path(output_file)
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_plantuml_command(
        command,
        plantuml_file,
        output.parent
    )

    run_plantuml(cmd)
    move_generated_svg(plantuml_file, output)

    return output
