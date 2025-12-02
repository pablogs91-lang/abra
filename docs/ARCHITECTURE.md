# Abra Architecture

## Overview

Abra is built as a professional Python package following PEP standards and best practices. This architecture ensures scalability, maintainability, and ease of deployment.

## Package Structure

```
abra/
├── __init__.py          # Package entry point with public API
├── config/              # Configuration and constants
│   ├── __init__.py
│   └── constants.py
├── core/                # Core PyTrends functionality
│   ├── __init__.py
│   └── pytrends.py
├── analysis/            # Analysis engines
│   ├── __init__.py
│   ├── serpapi/         # SerpAPI integration (8 modules)
│   ├── insights.py
│   ├── amazon.py
│   ├── youtube.py
│   └── ...
├── components/          # Reusable UI components
│   ├── __init__.py
│   ├── cards/
│   ├── charts/
│   ├── layouts/
│   ├── widgets/
│   └── render.py
├── ui/                  # Theming and styles
│   ├── __init__.py
│   ├── theme.py
│   └── styles.py
├── pages/               # Application pages/views
│   ├── __init__.py
│   ├── manual_search.py
│   ├── comparator.py
│   ├── historical.py
│   └── url_analysis.py
└── utils/               # Utility functions
    ├── __init__.py
    ├── helpers.py
    ├── sanitize.py
    └── export.py
```

## Key Design Principles

### 1. **Absolute Imports**
All imports use the `abra.` namespace:
```python
from abra.config.constants import COUNTRIES
from abra.ui.styles import apply_custom_css
from abra.pages.manual_search import render_manual_search
```

**Why**: Absolute imports are clearer, more explicit, and work reliably across all environments (local, Docker, Streamlit Cloud, etc.).

### 2. **Package Installation**
The app can be installed as a proper Python package:
```bash
pip install -e .          # Development mode
pip install abra          # From PyPI (future)
```

**Why**: This makes imports work everywhere without path manipulation and enables CLI tools.

### 3. **Modern Configuration**
Uses both `setup.py` (backwards compatibility) and `pyproject.toml` (modern standard).

**Why**: Maximum compatibility with all Python packaging tools.

### 4. **Separation of Concerns**
- **config/**: Constants and configuration
- **core/**: Business logic (PyTrends)
- **analysis/**: Analysis engines
- **components/**: UI building blocks
- **pages/**: Application views
- **ui/**: Presentation layer
- **utils/**: Helper functions

**Why**: Clear boundaries make the codebase easier to understand, test, and modify.

### 5. **Testability**
Structure allows easy unit testing:
```python
from abra.analysis.insights import calculate_trend_score

def test_trend_score():
    assert calculate_trend_score([1,2,3]) > 0
```

## Import Resolution

### How It Works

1. **Package Installation**: When you run `pip install -e .`, Python registers `abra` as an installed package
2. **Import Resolution**: `from abra.config import constants` works anywhere
3. **No Path Manipulation**: No need for `sys.path.insert()` or relative imports

### Example

```python
# app.py
from abra.config.constants import COUNTRIES  # ✅ Works
from abra.pages.manual_search import render_manual_search  # ✅ Works

# Inside abra/pages/manual_search.py
from abra.core.pytrends import get_trends  # ✅ Works
from abra.components.cards import Card  # ✅ Works
```

## Deployment

### Streamlit Cloud

1. **Requirements**: Just needs `requirements.txt`
2. **No special configuration**: Package installs automatically
3. **Imports work out of the box**: Because it's a proper package

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["streamlit", "run", "app.py"]
```

### Local Development

```bash
# One-time setup
pip install -e ".[dev]"

# Run
streamlit run app.py
```

## Scalability

### Adding New Features

1. **New Analysis Module**: Add to `abra/analysis/`
2. **New UI Component**: Add to `abra/components/`
3. **New Page**: Add to `abra/pages/`
4. **Import**: Use `from abra.analysis.new_module import ...`

### Adding CLI Tools

```python
# abra/cli.py
def main():
    """CLI entry point"""
    pass

# setup.py already configured:
# entry_points = {
#     "console_scripts": [
#         "abra=abra.cli:main",
#     ],
# }
```

Then use: `abra --help`

### Publishing to PyPI

```bash
make build        # Build distribution
make upload-test  # Test on TestPyPI
make upload       # Publish to PyPI
```

Then anyone can: `pip install abra`

## Benefits

1. ✅ **No import hacks**: Clean, professional imports
2. ✅ **Works everywhere**: Local, Docker, Cloud, etc.
3. ✅ **Testable**: Easy to write unit tests
4. ✅ **Scalable**: Add features without restructuring
5. ✅ **Publishable**: Can be distributed via PyPI
6. ✅ **Maintainable**: Clear structure, easy to navigate
7. ✅ **Professional**: Follows Python best practices

## Migration from src/

### Key Changes

1. **Directory**: `src/` → `abra/`
2. **Imports**: `from src.config` → `from abra.config`
3. **Installation**: Now installable with `pip install -e .`
4. **No path manipulation**: Removed all `sys.path.insert()` code

### Why This is Better

- **Before**: Fragile imports depending on execution context
- **After**: Rock-solid imports that work everywhere

The professional way is always the right way. 🚀
