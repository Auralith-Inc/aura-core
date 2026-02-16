"""Aura-Core: The Universal Context Compiler for AI Agent Memory"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auralith-aura",
    version="0.1.0",
    description="The Universal Context Compiler for AI Agent Memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Auralith Inc.",
    author_email="info@auralith.org",
    url="https://github.com/Auralith-Inc/aura-core",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "msgpack>=1.0.0",
        "safetensors>=0.3.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "docs": [
            "unstructured>=0.10.0",
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
        ],
        "data": [
            "pandas>=1.3.0",
            "openpyxl>=3.0.0",
            "pyarrow>=10.0.0",
        ],
        "all": [
            "unstructured[all-docs]>=0.10.0",
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
            "pandas>=1.3.0",
            "openpyxl>=3.0.0",
            "pyarrow>=10.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aura=aura.compiler:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="ai, agent-memory, rag, context-compiler, openclaw, claude-code, codex, gemini-cli, llm, knowledge-base",
)
