
"""Обработка аргументов командной строки."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Настройки запуска программы."""

    package: str
    version: str
    repository: str
    output: str
    depth: int
    filter_text: str
    test_mode: bool
    test_file: str
    load_order: bool
    framework: str
    plantuml: str


def create_parser():
    """Создаёт парсер аргументов командной строки."""

    parser = argparse.ArgumentParser(
        description="NuGet dependency graph visualizer"
    )

    parser.add_argument("--package", required=True)
    parser.add_argument("--version", default="")
    parser.add_argument(
        "--repository",
        default="https://api.nuget.org/v3-flatcontainer"
    )
    parser.add_argument("--output", default="output/graph.svg")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--filter", default="")
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--test-file", default="")
    parser.add_argument("--load-order", action="store_true")
    parser.add_argument("--framework", default="net8.0")
    parser.add_argument("--plantuml", default="plantuml.jar")

    return parser


def parse_arguments():
    """Читает аргументы и проверяет их корректность."""

    parser = create_parser()
    args = parser.parse_args()

    if args.depth < 0:
        parser.error("--depth cannot be negative")

    if not args.package.strip():
        parser.error("--package cannot be empty")

    if not args.output.lower().endswith(".svg"):
        parser.error("--output must have .svg extension")

    if args.test_mode:
        if not args.test_file:
            parser.error("--test-file is required in test mode")
        if not Path(args.test_file).is_file():
            parser.error("Test repository file does not exist")
    elif not args.version:
        parser.error("--version is required outside test mode")

    if not args.repository.startswith(("http://", "https://")):
        parser.error("--repository must be an HTTP(S) URL")

    return Settings(
        package=args.package.strip(),
        version=args.version.strip(),
        repository=args.repository.rstrip("/"),
        output=args.output,
        depth=args.depth,
        filter_text=args.filter,
        test_mode=args.test_mode,
        test_file=args.test_file,
        load_order=args.load_order,
        framework=args.framework,
        plantuml=args.plantuml
    )


def print_settings(settings):
    """Выводит все настройки в формате ключ-значение."""

    for key, value in vars(settings).items():
        print(f"{key}: {value}")