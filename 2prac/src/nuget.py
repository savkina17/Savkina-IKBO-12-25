
"""Получение и разбор метаданных NuGet."""

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from functools import total_ordering


@dataclass
class Dependency:
    """Описание одной зависимости NuGet."""

    package_id: str
    version_spec: str


@total_ordering
@dataclass(frozen=True)
class PackageVersion:
    """Упрощённое представление версии NuGet."""

    value: str

    def parts(self):
        """Возвращает числовые компоненты версии."""

        numbers = re.match(r"^\d+(?:\.\d+)*", self.value)
        if not numbers:
            return (0,)

        return tuple(int(x) for x in numbers.group().split("."))

    def __lt__(self, other):
        """Сравнивает версии по числовым компонентам."""

        return self.parts() < other.parts()


class NuGetClient:
    """Клиент для работы с NuGet Flat Container API."""

    def __init__(self, repository):
        """Сохраняет адрес NuGet-репозитория."""

        self.repository = repository.rstrip("/")

    def request(self, url):
        """Выполняет HTTP GET и возвращает содержимое."""

        print(f"HTTP GET: {url}")

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "DependencyVisualizer/1.0"}
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"HTTP error {error.code}: {url}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(
                f"Connection error: {error.reason}"
            ) from error

    def get_versions(self, package_id):
        """Получает опубликованные версии пакета."""

        url = (
            f"{self.repository}/{package_id.lower()}/index.json"
        )
        data = json.loads(self.request(url))
        return data["versions"]

    def resolve_version(self, package_id, specification):
        """Выбирает подходящую опубликованную версию."""

        if not specification:
            raise ValueError(
                f"Version is missing for {package_id}"
            )

        if not any(char in specification for char in "[](),*"):
            return specification

        versions = self.get_versions(package_id)
        selected = self.select_version(versions, specification)

        if selected is None:
            raise ValueError(
                f"No version satisfies {specification}"
            )

        print(
            f"  Версия {package_id}: "
            f"{specification} -> {selected}"
        )
        return selected

    @staticmethod
    def select_version(versions, specification):
        """Выбирает минимальную версию из диапазона."""

        if specification == "*":
            return max(
                versions,
                key=lambda value: PackageVersion(value)
            )

        match = re.fullmatch(
            r"([\[(])([^,]*)?(?:,([^]]*))?([\])])",
            specification
        )

        if not match:
            return None

        left, lower, upper, right = match.groups()

        if upper is None:
            lower = lower or ""
            upper = lower

        candidates = []

        for version in versions:
            current = PackageVersion(version)

            if lower:
                boundary = PackageVersion(lower)
                if current < boundary:
                    continue
                if current == boundary and left == "(":
                    continue

            if upper:
                boundary = PackageVersion(upper)
                if boundary < current:
                    continue
                if current == boundary and right == ")":
                    continue

            candidates.append(version)

        if not candidates:
            return None

        return min(candidates, key=lambda value: PackageVersion(value))

    def get_dependencies(self, package_id, version, framework):
        """Получает прямые зависимости из nuspec-файла."""

        url = (
            f"{self.repository}/{package_id.lower()}/"
            f"{version.lower()}/{package_id.lower()}.nuspec"
        )

        xml_data = self.request(url)
        root = ET.fromstring(xml_data)

        dependencies = self.find_dependency_group(root, framework)

        return dependencies

    @staticmethod
    def find_dependency_group(root, framework):
        """Выбирает группу зависимостей для целевой платформы."""

        groups = root.findall(".//{*}dependencies/{*}group")

        if not groups:
            return NuGetClient.parse_dependencies(
                root.findall(".//{*}dependencies/{*}dependency")
            )

        normalized = framework.lower()

        for group in groups:
            target = group.attrib.get("targetFramework", "").lower()

            if target == normalized:
                return NuGetClient.parse_dependencies(
                    group.findall("{*}dependency")
                )

        for group in groups:
            if not group.attrib.get("targetFramework"):
                return NuGetClient.parse_dependencies(
                    group.findall("{*}dependency")
                )

        # Если точного совпадения нет, используем первую группу.
        print(
            f"Предупреждение: группа {framework} не найдена. "
            "Используется первая доступная группа."
        )

        return NuGetClient.parse_dependencies(
            groups[0].findall("{*}dependency")
        )

    @staticmethod
    def parse_dependencies(elements):
        """Преобразует XML-элементы в объекты Dependency."""

        result = []

        for element in elements:
            package_id = element.attrib.get("id", "")
            version = element.attrib.get("version", "")

            if package_id:
                result.append(
                    Dependency(package_id, version)
                )

        return result