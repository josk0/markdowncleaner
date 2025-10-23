# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.3.0 - 2025-10-22

### Added
- **Heuristic reference removal**: Automatically detect and remove bibliographic reference lines based on pattern scoring
- **Batch processing script**: Process multiple markdown files in parallel with `scripts/clean_mds_in_folder.py`
- **Footnote pattern removal**: Remove footnote references in text (e.g., `.1`, `.23`)
- **Enhanced linebreak crimping**: Improved algorithm for fixing line break errors from PDF conversion
  - Connective-based crimping for lines ending with `-`, `–`, `—`, or `...`
  - Justified text crimping for adjacent lines of similar length
- **CLI options**:
  - `--keep-references`: Disable heuristic reference detection
  - `--no-crimping`: Disable linebreak crimping
  - Additional fine-grained control options for cleaning operations

### Changed
- **Default patterns**: Updated `default_cleaning_patterns.yaml` with:
  - Improved section removal patterns (e.g., "Authors' Note", "Note on sources")
  - Additional inline patterns (LaTeX footnotes, trailing ellipsis)
  - Refined keyword and conflict of interest patterns
- **API**: `MarkdownCleaner` constructor `patterns` parameter is now annotated as optional (defaults to None for default patterns)
- **Linebreak crimping**: Now enabled by default (`crimp_linebreaks: True`)
- **README**: Updates with new features and examples

### Fixed
- Linebreak crimping logic now properly handles various PDF conversion artifacts. In previous version it crimped together too happily
- Test suite updated to match new implementation, mostly just fixing parameter names; bit lazy on adding tests

## [0.2.0] - 2025-03-03

Initial PyPI release with core markdown cleaning functionality.

### Features
- Remove references, bibliographies, and citations
- Remove copyright notices and legal disclaimers
- Remove acknowledgements and funding information
- Pattern-based text cleaning with customizable YAML configuration
- Command-line interface
- Python API for programmatic use
- Text replacement and pattern removal
- Duplicate headline removal
- Short line removal
- Empty line contraction
- Encoding fix support (mojibake)
- Quotation normalization
