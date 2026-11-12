# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.4.0 - 2026-11-12

This release fixes several default patterns and heuristics that silently damaged or deleted legitimate text. Cleaned output will differ from 0.3.1.

### Fixed
- **Footnote removal no longer corrupts numbers**: decimals and numbered references are kept (`3.14`, `version 3.5`, `Eq. 2 shows`, `Ref. 12 Theorem`); footnote markers such as `claim.12 The` are still removed
- `\footnote{...}` is removed without inserting a sentence break
- **Heading detection**: a heading needs a space after its hashes (`#tag` is text), may be indented up to 3 spaces, and may have a closing sequence (`## References ##`). Completes the heading-level fix from 0.3.1, which covered only one of two places. Applies to section removal, duplicate-headline removal, short-line removal and line joining
- **Code blocks are left intact**: short-line removal, whole-line removal, space collapsing and line joining skip fenced code, so a `# comment` in code no longer starts or ends section removal. A line like ` ```x``` ` does not open a fence, and an unclosed fence is ignored
- **Line joining** keeps en and em dashes (`time—` + `and` → `time—and`), skips at most 2 blank lines, and does not join `---` dividers
- **Quote normalization** converts curly quotes (`‘ ’ “ ”`) again, and leaves backticks alone
- Default patterns that deleted ordinary prose: the ALL-CAPS line rule ignored case, `c \d{4}` matched inside words (`democratic 1960s`), `(see` matched `(seemingly`
- Default patterns that never matched: `ACM Reference Format`, `author(s) received/declared`
- Config loading: empty or null keys load as empty, non-list values raise a clear error, replacement values are no longer stripped, and `get_default_patterns()` returns a fresh copy so callers cannot change each other's patterns

### Changed
- Requires `pyyaml>=6.0.1` (6.0 cannot be built on current Python versions)
- Tested on Python 3.10 to 3.15, and with the lowest allowed dependency versions

## 0.3.1 - 2025-12-28

### Fixed
- **Heading level detection**: Fixed bug in `_remove_sections` that incorrectly counted all `#` characters instead of only leading ones
- Fixed typo in CleanerOptions docstring ("Countainer" → "Container")

### Changed
- **Performance**: Quote normalization regexes now compiled once at module load instead of on each call
- **Code organization**: Moved `_is_list_item` helper to module level; use dataclass constructor in CLI

### Added
- Comprehensive regression test suite for all default patterns (test_pattern_regression.py)
- CONTRIBUTING.md with contribution guidelines

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
