"""
Sokkary V2 - AI Multi-Agent System
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sokkary-v2",
    version="0.1.0",
    author="mhdessouky-creator",
    description="AI Multi-Agent System with LangGraph, MCP, Tools, and Skills",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhdessouky-creator/sokkary-v2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "pytest-asyncio>=0.25.2",
            "pytest-cov>=6.0.0",
            "ruff>=0.9.1",
            "black>=24.12.0",
            "mypy>=1.14.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "sokkary=cli.main:main",
        ],
    },
)
