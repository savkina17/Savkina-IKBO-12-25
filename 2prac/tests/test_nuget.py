
"""Тесты обработки NuGet-версий и XML."""

import xml.etree.ElementTree as et

from src.nuget import NuGetClient, PackageVersion


def test_exact_version():
    """Проверяет выбор точной версии."""

    result = NuGetClient.select_version(
        ["1.0.0", "2.0.0"],
        "[1.0.0]"
    )

    assert result == "1.0.0"


def test_version_range():
    """Проверяет выбор версии из диапазона."""

    result = NuGetClient.select_version(
        ["1.0.0", "1.5.0", "2.0.0"],
        "[1.0.0,2.0.0)"
    )

    assert result == "1.0.0"


def test_version_comparison():
    """Проверяет сравнение числовых компонентов версий."""

    assert PackageVersion("2.0.0") > PackageVersion("1.9.0")


def test_parse_dependencies():
    """Проверяет извлечение зависимостей из XML."""

    xml = """
    <dependencies>
        <dependency id="Example" version="1.0.0" />
    </dependencies>
    """

    root = et.fromstring(xml)
    elements = root.findall(".//dependency")
    result = NuGetClient.parse_dependencies(elements)

    assert len(result) == 1
    assert result[0].package_id == "Example"
    assert result[0].version_spec == "1.0.0"


def test_framework_group():
    """Проверяет выбор группы целевой платформы."""

    xml = """
    <package>
        <metadata>
            <dependencies>
                <group targetFramework="net8.0">
                    <dependency id="Modern" version="1.0" />
                </group>
                <group targetFramework="net6.0">
                    <dependency id="Old" version="2.0" />
                </group>
            </dependencies>
        </metadata>
    </package>
    """

    root = et.fromstring(xml)
    result = NuGetClient.find_dependency_group(root, "net8.0")

    assert result[0].package_id == "Modern"
