# Contributing

Contributions are welcome! Here's how to get started:

## Setup

```bash
git clone https://github.com/josk0/markdowncleaner.git
cd markdowncleaner
pip install -e .
```

## Running Tests

```bash
python -m pytest tests/
```

## Submitting Changes

1. Fork the repo and create a branch
2. Make your changes and add tests if needed
3. Make sure tests pass
4. Open a PR

## Adding Cleaning Patterns

New patterns go in `src/markdowncleaner/config/default_cleaning_patterns.yaml`. Please add a test case in `tests/test_pattern_regression.py`.

## Questions?

Open an issue!
