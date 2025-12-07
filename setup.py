#!/usr/bin/env python3
"""
Setup script for modpack-installer.
For modern installations, use pyproject.toml with pip.
This file is kept for backward compatibility.
"""

from setuptools import setup

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="modpack-installer",
    version="2.3.5",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
