# markdowncleaner

A simple Python tool for cleaning and formatting markdown documents. Default configuration with regex patterns for PDFs of academic papers that have been converted to markdown.

I use this myself in a workflow that processes academic PDFs using [docling](https://github.com/docling-project/docling) or [olmOCR](https://github.com/allenai/olmocr). The default configuration fits that use case.

## Description

`markdowncleaner` removes unwanted content such as:
- References, bibliographies, and citations (including heuristic detection of bibliographic lines)
- Footnotes and endnote references in text
- Copyright notices and legal disclaimers
- Acknowledgements and funding information
- Author information and contact details
- Specific patterns like DOIs, URLs, and email addresses
- Short lines and excessive whitespace
- Duplicate headlines (for example, because paper title and author names were reprinted on every page of a PDF)
- Erroneous line breaks from PDF conversion

## Installation

Requires Python 3.10 or higher.

```bash
pip install markdowncleaner
```

## Usage

### Python API

#### Basic Usage

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

#### Customizing Cleaning Options

```python
from markdowncleaner import MarkdownCleaner, CleanerOptions

# Create custom options
options = CleanerOptions()
options.remove_short_lines = True
options.min_line_length = 50  # custom minimum line length
options.remove_duplicate_headlines = False
options.remove_footnotes_in_text = True
options.contract_empty_lines = True
options.fix_encoding_mojibake = True
options.normalize_quotation_symbols = True

# Initialize cleaner with custom options
cleaner = MarkdownCleaner(options=options)

# Use the cleaner as before
```

#### Custom Cleaning Patterns

You can also provide custom cleaning patterns:

```python
from markdowncleaner import MarkdownCleaner
from markdowncleaner.config.loader import CleaningPatterns
from pathlib import Path

# Load custom patterns from a YAML file
custom_patterns = CleaningPatterns.from_yaml(Path("my_patterns.yaml"))

# Initialize cleaner with custom patterns
cleaner = MarkdownCleaner(patterns=custom_patterns)
```

### Command Line Interface

Clean a single markdown file using the CLI:

```bash
# Basic usage - creates a new file with "_cleaned" suffix
markdowncleaner input.md

# Specify output file
markdowncleaner input.md -o output.md

# Specify output directory
markdowncleaner input.md --output-dir cleaned_files/

# Use custom configuration
markdowncleaner input.md --config my_patterns.yaml

# Enable encoding fixes and quotation normalization
markdowncleaner input.md --fix-encoding --normalize-quotation

# Customize line length threshold
markdowncleaner input.md --min-line-length 50

# Disable specific cleaning operations
markdowncleaner input.md --keep-short-lines --keep-sections --keep-footnotes

# Disable replacements and inline pattern removal
markdowncleaner input.md --no-replacements --keep-inline-patterns

# Disable formatting operations
markdowncleaner input.md --no-crimping --keep-empty-lines

# Keep references (disable heuristic reference detection)
markdowncleaner input.md --keep-references
```

**Available CLI Options:**

- `-o`, `--output`: Path to save the cleaned markdown file
- `--output-dir`: Directory to save the cleaned file
- `--config`: Path to custom YAML configuration file
- `--fix-encoding`: Fix encoding mojibake issues
- `--normalize-quotation`: Normalize quotation symbols to standard ASCII
- `--keep-short-lines`: Don't remove lines shorter than minimum length
- `--min-line-length`: Minimum line length to keep (default: 70)
- `--keep-bad-lines`: Don't remove lines matching bad line patterns
- `--keep-sections`: Don't remove sections like References, Acknowledgements
- `--keep-duplicate-headlines`: Don't remove duplicate headlines
- `--keep-footnotes`: Don't remove footnote references in text
- `--no-replacements`: Don't perform text replacements
- `--keep-inline-patterns`: Don't remove inline patterns like citations
- `--keep-empty-lines`: Don't contract consecutive empty lines
- `--no-crimping`: Don't crimp linebreaks (fix line break errors from PDF conversion)
- `--keep-references`: Don't heuristically detect and remove bibliographic reference lines

### Batch Processing Script

For processing multiple markdown files in a folder and its subfolders, use the included batch processing script:

```bash
# Basic usage - will prompt for confirmation
python scripts/clean_mds_in_folder.py documents/

# Skip confirmation prompt
python scripts/clean_mds_in_folder.py documents/ --yes

# Use 8 parallel workers (default is your CPU count)
python scripts/clean_mds_in_folder.py documents/ --workers 8

# Use custom cleaning patterns
python scripts/clean_mds_in_folder.py documents/ --config my_patterns.yaml

# Combine options
python scripts/clean_mds_in_folder.py documents/ --yes --workers 4
```

**Features:**
- Recursively finds all `.md` files in the specified folder and subfolders
- Processes files in parallel using multiple CPU cores for faster processing
- Shows real-time progress bar with `tqdm`
- Cleans files in-place (modifies original files)
- Asks for confirmation before processing (unless `--yes` is used)
- Continues processing even if some files fail
- Reports all successful and failed files at the end

**Script Options:**
- `folder`: Path to folder containing markdown files (required)
- `-y`, `--yes`: Skip confirmation prompt and proceed immediately
- `-w`, `--workers`: Number of parallel workers (default: CPU count)
- `--config`: Path to custom YAML configuration file

**Note:** Requires `tqdm` for the progress bar:
```bash
pip install tqdm
```

## Configuration

The default cleaning patterns are defined in `default_cleaning_patterns.yaml` and include:

- **Sections to Remove**: Acknowledgements, References, Bibliography, etc.
- **Bad Inline Patterns**: Citations, figure references, etc.
- **Bad Lines Patterns**: Copyright notices, DOIs, URLs, etc.
- **Footnote Patterns**: Footnote references in text that fit the pattern '.1'
- **Replacements**: Various character replacements for PDF parsing errors

## Options

All available `CleanerOptions`:

- `fix_encoding_mojibake`: Fix encoding issues and mojibake using ftfy (default: False)
- `normalize_quotation_symbols`: Normalize various quotation marks to standard ASCII quotes (default: False)
- `remove_short_lines`: Remove lines shorter than `min_line_length` (default: True)
- `min_line_length`: Minimum line length to keep when `remove_short_lines` is enabled (default: 70)
- `remove_whole_lines`: Remove lines matching specific patterns (default: True)
- `remove_sections`: Remove entire sections based on section headings (default: True)
- `remove_duplicate_headlines`: Remove duplicate headlines based on threshold (default: True)
- `remove_duplicate_headlines_threshold`: Number of occurrences needed to consider a headline duplicate (default: 2)
- `remove_footnotes_in_text`: Remove footnote references like ".1" or ".23" (default: True)
- `replace_within_lines`: Replace specific patterns within lines (default: True)
- `remove_within_lines`: Remove specific patterns within lines (default: True)
- `contract_empty_lines`: Reduce multiple consecutive empty lines to one (default: True)
- `crimp_linebreaks`: Fix line break errors from PDF conversion (default: True)
- `remove_references_heuristically`: Heuristically detect and remove bibliographic reference lines by scoring lines based on bibliographic patterns (default: True)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.