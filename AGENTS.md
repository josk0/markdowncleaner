# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Install in development mode
pip install -e .

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_cleaner.py

# Run a specific test
python -m pytest tests/test_cleaner.py::TestMarkdownCleaner::test_remove_short_lines

# Use the CLI after installation
markdowncleaner input.md -o output.md
```

## Architecture

This is a Python package for cleaning markdown documents, particularly academic papers converted from PDF.

### Core Components

- **`src/markdowncleaner/markdowncleaner.py`**: Main `MarkdownCleaner` class and `CleanerOptions` dataclass. The `clean_markdown_string()` method applies cleaning operations in this order:
  1. Encoding fixes (ftfy)
  2. Heuristic bibliographic line removal (scoring-based)
  3. Multiple space reduction (always applied)
  4. Quote normalization
  5. Short line removal
  6. Bad line pattern removal
  7. Section removal (References, Acknowledgements, etc.)
  8. Duplicate headline removal
  9. Text replacements (GLYPH fixes, etc.)
  10. Footnote removal
  11. Inline pattern removal
  12. Line break crimping (rejoining PDF-broken lines)
  13. Empty line contraction

- **`src/markdowncleaner/config/loader.py`**: `CleaningPatterns` dataclass that loads regex patterns from YAML. Uses `get_default_patterns()` with caching.

- **`src/markdowncleaner/config/default_cleaning_patterns.yaml`**: Default regex patterns for sections, inline patterns, whole lines, footnotes, and character replacements.

- **`src/markdowncleaner/cli.py`**: Command-line interface using argparse. Maps CLI flags to `CleanerOptions`.

### Key Design Patterns

- Patterns are compiled once and cached via `_cached_patterns` global
- All cleaning operations are toggleable via `CleanerOptions` booleans
- The bibliographic line scorer (`_score_bibliography_line`) uses a point system to detect reference lines without relying on section headers
- Line crimping handles both hyphenated word breaks and justified text reflow
