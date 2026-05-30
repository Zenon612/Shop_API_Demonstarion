#!/usr/bin/env python
"""Setup script for demo-shop-api."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="demo-shop-api",
    version="1.1.0",
    author="Demo",
    author_email="demo@example.com",
    description="Demo FastAPI backend project with PostgreSQL, Redis, Celery, and Kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/demo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0",
            "black==23.12.1",
            "isort==5.13.2",
            "mypy==1.7.1",
        ]
    },
)
