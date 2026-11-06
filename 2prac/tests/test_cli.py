
"""Тесты командной строки."""

import sys

import pytest

from src.cli import parse_arguments


def test_valid_arguments(monkeypatch):
    """Проверяет корректный набор аргументов."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--package", "Example",
            "--version", "1.0.0"
        ]
    )

    settings = parse_arguments()

    assert settings.package == "Example"
    assert settings.version == "1.0.0"


def test_negative_depth(monkeypatch):
    """Проверяет запрет отрицательной глубины."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--package", "Example",
            "--version", "1.0",
            "--depth", "-1"
        ]
    )

    with pytest.raises(SystemExit):
        parse_arguments()


def test_missing_version(monkeypatch):
    """Проверяет обязательность версии в обычном режиме."""

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--package", "Example"]
    )

    with pytest.raises(SystemExit):
        parse_arguments()