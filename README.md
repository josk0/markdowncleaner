# markdowncleaner

A simple Python tool for cleaning and formatting markdown documents. Default configuration with regex patterns for PDFs of academic papers that have been converted to markdown.

## Description

`markdowncleaner` helps you clean up markdown files by removing unwanted content such as:
- References, bibliographies, and citations
- Footnotes and endnote references in text
- Copyright notices and legal disclaimers
- Acknowledgements and funding information
- Author information and contact details
- Specific patterns like DOIs, URLs, and email addresses
- Short lines and excessive whitespace
- Duplicate headlines (for example, because paper title and author names were reprinted on every page of a PDF)

This tool is particularly useful for processing academic papers, books, or any markdown document that needs formatting cleanup.

## Installation

```bash
pip install markdowncleaner
```

## Usage

### Basic Usage

```python
from markdowncleaner import MarkdownCleaner
from pathlib import Path

# Create a cleaner with default patterns
cleaner = MarkdownCleaner()

# Clean a markdown file
result_path = cleaner.clean_markdown_file(Path("input.md"))

# Clean a markdown string
text = "# Title\nSome content here. [1]\n\nReferences\n1. Citation"
cleaned_text = cleaner.clean_markdown_string(text)
print(cleaned_text)
```

### Customizing Cleaning Options

```python
from markdowncleaner import MarkdownCleaner, CleanerOptions

# Create custom options
options = CleanerOptions()
options.remove_short_lines = True
options.min_line_length = 50  # custom minimum line length
options.remove_duplicate_headlines = False 
options.remove_footnotes_in_text = True
options.contract_empty_lines = True

# Initialize cleaner with custom options
cleaner = MarkdownCleaner(options=options)

# Use the cleaner as before
```

### Custom Cleaning Patterns

You can also provide custom cleaning patterns:

```python
from markdowncleaner import MarkdownCleaner, CleaningPatterns
from pathlib import Path

# Load custom patterns from a YAML file
custom_patterns = CleaningPatterns.from_yaml(Path("my_patterns.yaml"))

# Initialize cleaner with custom patterns
cleaner = MarkdownCleaner(patterns=custom_patterns)
```

## Configuration

The default cleaning patterns are defined in `default_cleaning_patterns.yaml` and include:

- **Sections to Remove**: Acknowledgements, References, Bibliography, etc.
- **Bad Inline Patterns**: Citations, figure references, etc.
- **Bad Lines Patterns**: Copyright notices, DOIs, URLs, etc.
- **Footnote Patterns**: Footnote references in text that fit the pattern '.1'
- **Replacements**: Various character replacements for PDF parsing errors

## Options

- `remove_short_lines`: Remove lines shorter than `min_line_length` (default: 70 characters)
- `remove_whole_lines`: Remove lines matching specific patterns
- `remove_sections`: Remove entire sections based on section headings
- `remove_duplicate_headlines`: Remove duplicate headlines based on threshold
- `remove_duplicate_headlines_threshold`: Threshold for duplicate headline removal
- `remove_footnotes_in_text`: Remove footnote references
- `replace_within_lines`: Replace specific patterns within lines
- `remove_within_lines`: Remove specific patterns within lines
- `contract_empty_lines`: Normalize whitespace
- `crimp_linebreaks`: Improve line break formatting

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.