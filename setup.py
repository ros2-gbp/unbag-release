# MIT License
#
# Copyright (c) 2026 Institute for Automotive Engineering (ika), RWTH Aachen University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
import xml.etree.ElementTree as ET

from setuptools import find_packages, setup


def _read_package_metadata() -> tuple[str, str]:
    """
    Read the package version and description from ``package.xml``.

    Returns:
        tuple[str, str]: Version and description strings.
    """
    root = ET.fromstring(Path("package.xml").read_text(encoding="utf-8"))
    version = root.findtext("version")
    description = root.findtext("description")
    if not version or not description:
        raise RuntimeError("package.xml must define both <version> and <description>.")
    return version.strip(), description.strip()


PACKAGE_VERSION, PACKAGE_DESCRIPTION = _read_package_metadata()


setup(
    name="unbag",
    version=PACKAGE_VERSION,
    description=PACKAGE_DESCRIPTION,
    license="MIT",
    packages=find_packages(include=["ros2_unbag", "ros2_unbag.*"]),
    entry_points={
        "ros2cli.command": [
            "unbag = ros2_unbag.export:ExportCommand",
        ],
        "ros2cli.extension_point": [
            "unbag = ros2cli.command:CommandExtension",
        ],
    },
)
