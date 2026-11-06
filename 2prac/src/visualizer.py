
"""Формирование PlantUML и генерация SVG."""

import subprocess
from pathlib import Path


def generate_plantuml(graph, output_file):
    """Преобразует граф в текстовую диаграмму PlantUML."""

    vertices = sorted(graph.vertices())
    identifiers = {
        vertex: f"N{index}"
        for index, vertex in enumerate(vertices)
    }

    lines = ["@startuml", "left to right direction"]

    for vertex in vertices:
        label = vertex.replace('"', "'")
        lines.append(
            f'object "{label}" as {identifiers[vertex]}'
        )

    for parent, child in sorted(graph.edges()):
        source = identifiers[parent]
        target = identifiers[child]
        lines.append(f"{source} --> {target}")

    lines.append("@enduml")

    path = Path(output_file).with_suffix(".puml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return path



def generate_svg(plantuml_file, output_file, command):
    """Запускает PlantUML и сохраняет SVG."""

    output = Path(output_file)
    output.parent.mkdir(parents=True, exist_ok=True)

    if command.lower().endswith(".jar"):
        cmd = [
            "java",
            "-jar",
            command,
            "-tsvg",
            str(plantuml_file.resolve()),
            "-o",
            str(output.parent.resolve())
        ]
    else:
        cmd = [
            command,
            "-tsvg",
            str(plantuml_file.resolve()),
            "-o",
            str(output.parent.resolve())
        ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"PlantUML error: {result.stderr}"
        )

    generated = output.parent / (
        plantuml_file.stem + ".svg"
    )

    if generated != output and generated.exists():
        generated.replace(output)

    if not output.is_file():
        raise RuntimeError("SVG file was not generated")

    return output
