"""
Setup configuration for Abra - Advanced Brand Research & Analysis
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="abra",
    version="11.1.0",
    description="Advanced Brand Research & Analysis - Multi-channel trend analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Abra Team",
    author_email="",
    url="https://github.com/tu-usuario/abra",
    packages=find_packages(where=".", exclude=["tests", "docs"]),
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pytrends>=4.9.2",
        "plotly>=5.14.0",
        "reportlab>=4.0.0",
        "requests>=2.31.0",
        "google-search-results>=2.4.2",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "abra=abra.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="brand-analysis, market-research, google-trends, serpapi, competitive-intelligence",
    project_urls={
        "Bug Reports": "https://github.com/tu-usuario/abra/issues",
        "Source": "https://github.com/tu-usuario/abra",
        "Documentation": "https://github.com/tu-usuario/abra/blob/main/README.md",
    },
)
