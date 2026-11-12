import unittest
from pathlib import Path
import tempfile
import shutil
from markdowncleaner.markdowncleaner import MarkdownCleaner, CleanerOptions
from markdowncleaner.config.loader import get_default_patterns


class TestMarkdownCleaner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        # Initialize cleaner with default options
        self.cleaner = MarkdownCleaner(patterns=get_default_patterns())

    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)

    def test_remove_short_lines(self):
        text = "This is a long line that should be kept in the output.\n" + \
               "Short line.\n" + \
               "Another long line that should remain in the cleaned output."

        # Test with default settings (should remove short lines)
        result = self.cleaner._remove_short_lines(text, 50)
        self.assertIn("This is a long line", result)
        self.assertNotIn("Short line", result)

        # Test with option disabled
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)
        result = cleaner_with_options.clean_markdown_string(text)
        self.assertIn("Short line", result)

    def test_remove_whole_lines(self):
        text = "Normal content line.\n" + \
               "Copyright © 2023 All rights reserved.\n" + \
               "Another normal line."

        # Should remove the copyright line with default patterns, disabling short line removal for test
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)
        result = cleaner_with_options.clean_markdown_string(text)
        self.assertIn("Normal content line", result)
        self.assertNotIn("Copyright", result)

    def test_remove_sections(self):
        text = "# Introduction\n" + \
               "This is the introduction text.\n\n" + \
               "# References\n" + \
               "1. Author, A. (2023). Title. Journal.\n" + \
               "2. Another reference.\n\n" + \
               "# Conclusion\n" + \
               "This is the conclusion."

        # Should remove the References section
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("# Introduction", result)
        self.assertIn("# Conclusion", result)
        self.assertNotIn("# References", result)
        self.assertNotIn("1. Author", result)

    def test_remove_sections_keeps_same_level_heading_with_hash(self):
        # '## C# guide' is a level-2 heading: '#' inside the title must not
        # count toward the heading level, or the section is wrongly swallowed.
        text = "## remove-me\n" + \
               "body text here\n" + \
               "## C# guide\n" + \
               "kept content here\n"

        result = self.cleaner._remove_sections(text, "remove-me")
        self.assertNotIn("remove-me", result)
        self.assertNotIn("body text here", result)
        self.assertIn("## C# guide", result)
        self.assertIn("kept content here", result)

    def test_remove_sections_ignores_hash_without_space(self):
        # '#tag' is not a heading (CommonMark needs a space after the hashes),
        # so it must neither end a removed section nor be matched as a title.
        text = "## remove-me\n" + \
               "body text here\n" + \
               "#remove-me too\n" + \
               "more body\n" + \
               "## Next\n" + \
               "kept content here\n"

        result = self.cleaner._remove_sections(text, "remove-me")
        self.assertNotIn("body text here", result)
        self.assertNotIn("more body", result)
        self.assertIn("## Next", result)
        self.assertIn("kept content here", result)

        result = self.cleaner._remove_sections("#remove-me\nkept\n", "remove-me")
        self.assertIn("#remove-me", result)
        self.assertIn("kept", result)

    def test_remove_sections_ignores_hash_lines_in_code_fence(self):
        # A '# comment' inside a fenced code block must not end the section.
        text = "## remove-me\n" + \
               "```python\n" + \
               "# a comment\n" + \
               "x = 1\n" + \
               "```\n" + \
               "body after code\n" + \
               "## Next\n" + \
               "kept content here\n"

        result = self.cleaner._remove_sections(text, "remove-me")
        self.assertNotIn("# a comment", result)
        self.assertNotIn("body after code", result)
        self.assertIn("## Next", result)
        self.assertIn("kept content here", result)

    def test_remove_sections_keeps_code_fence_comment_matching_pattern(self):
        # A '# remove-me' comment inside a code fence must not start a removal.
        text = "## Intro\n" + \
               "~~~\n" + \
               "# remove-me\n" + \
               "code line\n" + \
               "~~~\n" + \
               "kept content here\n"

        result = self.cleaner._remove_sections(text, "remove-me")
        self.assertIn("# remove-me", result)
        self.assertIn("code line", result)
        self.assertIn("kept content here", result)

    def test_remove_sections_unclosed_fence_does_not_hide_headings(self):
        # A stray '```' that never closes must not swallow the rest of the text.
        text = "## remove-me\n" + \
               "```\n" + \
               "body text here\n" + \
               "## Next\n" + \
               "kept content here\n"

        result = self.cleaner._remove_sections(text, "remove-me")
        self.assertNotIn("body text here", result)
        self.assertIn("## Next", result)
        self.assertIn("kept content here", result)

    def test_contract_empty_lines(self):
        text = "Line 1\n\n\n\nLine 2"
        result = self.cleaner._contract_empty_lines(text)
        self.assertEqual(result, "Line 1\n\nLine 2")

    def test_replace_within_lines(self):
        text = "This text contains [1] a citation reference."
        # Use a pattern that matches citation markers
        result = self.cleaner._replace_within_lines(text, r'\[\d+\]', '')
        self.assertEqual(result, "This text contains  a citation reference.")

    def test_remove_footnotes(self):
        text = ".1 Footnote\n" + \
               "Normal Line 1.\n\n" + \
               "Another line" + \
               ".18 Footnote.\n" + \
               ". 191 Stranger Footnote.\n\n" + \
               "Normal line" + \
               ". A Funny line"

        # disabling short line removal for test
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)

        result = cleaner_with_options.clean_markdown_string(text)
        self.assertTrue("Normal Line 1." in result)
        self.assertTrue(". A Funny line" in result)
        self.assertFalse(".1 Footnote" in result)

    def test_remove_duplicate_headlines(self):
        """Test all headline removal scenarios in a single test function."""
        # Test with an empty string
        self.assertEqual(self.cleaner._remove_duplicate_headlines(""), "")

        # Test with text that contains no headlines
        text_no_headlines = "This is just regular text\nwith no headlines at all."
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_no_headlines), text_no_headlines)

        # Test with text that contains unique headlines
        text_unique = "# Headline 1\nSome content\n## Headline 2\nMore content\n# Headline 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_unique), text_unique)

        # Test with text that contains duplicate headlines
        text_duplicate = "# Duplicate\n" +\
                        "Content 1\n" +\
                        "# Unique\nContent 2\n" +\
                        "# Duplicate\n" +\
                        "Content 3"
        expected_duplicate = "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "Content 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_duplicate), expected_duplicate)

        # Test with empty lines
        text_with_empty_lines = "# Duplicate\n" +\
                        "\n" +\
                        "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "\n" +\
                        "\n" +\
                        "# Duplicate\n" +\
                        "Content 3"
        expected_with_empty_lines = "\n" +\
                        "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "\n" +\
                        "\n" +\
                        "Content 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_with_empty_lines), expected_with_empty_lines)

        # Test with different headline levels where some are duplicates
        text_mixed_levels = "# Level 1\n" +\
                            "Content\n" +\
                            "## Level 2\n" +\
                            "More content\n" +\
                            "# Level 1\n" +\
                            "More content\n" +\
                            "### Level 3"
        expected_mixed_levels = "Content\n" +\
                            "## Level 2\n" +\
                            "More content\n" +\
                            "More content\n" +\
                            "### Level 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_mixed_levels), expected_mixed_levels)

        # Test with multiple sets of duplicate headlines
        text_multiple_dups = "# H1\n" +\
                            "A\n" +\
                            "## H2\n" +\
                            "B\n" +\
                            "# H1\n" +\
                            "C\n" +\
                            "## H2\n" +\
                            "D\n" +\
                            "### H3\n" +\
                            "E"
        expected_multiple_dups = "A\n" +\
                            "B\n" +\
                            "C\n" +\
                            "D\n" +\
                            "### H3\n" +\
                            "E"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_multiple_dups), expected_multiple_dups)

        # Test that headline matching is case-sensitive
        text_case = "# Headline\n" +\
                    "Content\n" +\
                    "# headline\n" +\
                    "More content"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_case), text_case)

    def test_remove_short_lines_treats_hash_without_space_as_text(self):
        # '#tag' is not a heading, so a short '#tag' line is removed like other short text.
        text = "#tag\n## Short heading\nA long line of body text that is clearly long enough to stay."
        result = self.cleaner._remove_short_lines(text, 50)
        self.assertNotIn("#tag", result)
        self.assertIn("## Short heading", result)

    def test_remove_duplicate_headlines_ignores_hash_without_space(self):
        # Repeated '#include' lines are not headlines and must be kept.
        text = "#include <stdio.h>\n## Title\ntext\n#include <stdio.h>\n## Title"
        result = self.cleaner._remove_duplicate_headlines(text)
        self.assertEqual(result.count("#include <stdio.h>"), 2)
        self.assertNotIn("## Title", result)

    def test_remove_duplicate_headlines_ignores_code_fence_comments(self):
        # A '# comment' repeated inside code blocks is code, not a headline.
        text = "## Title\n```python\n# setup\nx = 1\n```\n## Title\n~~~\n# setup\n~~~"
        result = self.cleaner._remove_duplicate_headlines(text)
        self.assertEqual(result.count("# setup"), 2)
        self.assertNotIn("## Title", result)

    def test_crimp_linebreaks_joins_line_starting_with_hash_without_space(self):
        # A justified line that starts with '#tag' is text, not a heading, so it is joined.
        first = "#hashtag opens this justified line of body text that runs on long enough here"
        second = "and this second justified line continues the same long sentence up to its end."
        result = self.cleaner._crimp_linebreaks(first + "\n" + second)
        self.assertEqual(result, first + " " + second)

        heading = "## A heading that opens with hashes and runs long enough to look justified"
        result = self.cleaner._crimp_linebreaks(heading + "\n" + second)
        self.assertEqual(result, heading + "\n" + second)

    def test_crimp_linebreaks(self):
        # Test connective-based crimping (line ending with hyphen)
        text = "This line ends with a hy-\nphenated word that continues."
        result = self.cleaner._crimp_linebreaks(text)
        self.assertEqual(result, "This line ends with a hyphenated word that continues.")

    def test_clean_markdown_file(self):
        # Create a test markdown file
        test_file = self.test_dir / "test.md"
        test_content = "# Test Document\nThis is a test.\n\n# References\n1. Test reference."

        with open(test_file, 'w') as f:
            f.write(test_content)

        # Clean the file
        output_file = self.cleaner.clean_markdown_file(test_file, self.test_dir)

        # Verify output exists
        self.assertTrue(output_file.exists())

        # Verify content was cleaned
        with open(output_file) as f:
            content = f.read()
            self.assertIn("# Test Document", content)
            self.assertNotIn("# References", content)


BODY = "This paragraph is substantive body text that is long enough to keep in the output. "


def _only(**on):
    """CleanerOptions with every step off except the named ones."""
    opts = CleanerOptions(remove_short_lines=False, remove_whole_lines=False, remove_sections=False,
                          remove_duplicate_headlines=False, remove_footnotes_in_text=False,
                          replace_within_lines=False, remove_within_lines=False,
                          contract_empty_lines=False, crimp_linebreaks=False,
                          remove_references_heuristically=False)
    for k, v in on.items():
        setattr(opts, k, v)
    return opts


class TestReviewFixes(unittest.TestCase):
    """Regression tests for bugs found in the 2026-11 code review."""

    def setUp(self):
        self.cleaner = MarkdownCleaner()

    # A1: fences and indented headings survive short-line removal
    def test_code_fence_protects_heading_like_comment_in_default_pipeline(self):
        doc = ("# Intro\n" + BODY + "\n```python\n# References\nx = 1\n```\n"
               + BODY.replace("substantive", "after-code") + "\n# Conclusion\n" + BODY)
        result = self.cleaner.clean_markdown_string(doc)
        self.assertIn("after-code", result)
        self.assertIn("```python", result)
        self.assertIn("x = 1", result)

    def test_short_line_removal_keeps_indented_heading(self):
        result = self.cleaner._remove_short_lines("  ## Heading\n" + BODY, 70)
        self.assertIn("  ## Heading", result)

    def test_four_space_indented_hash_is_not_a_heading(self):
        text = "# Intro\ntext\n    # References\ncode\n# Next\n"
        result = self.cleaner._remove_sections(text, "References")
        self.assertIn("code", result)

    # A2: a line like ```x``` does not open a fence
    def test_inline_triple_backticks_do_not_open_fence(self):
        text = "```x``` inline\n# References\nref\n```\n# Next\nkept\n"
        result = self.cleaner._remove_sections(text, "References")
        self.assertNotIn("ref\n", result)
        self.assertIn("kept", result)

    # A3: footnote pattern spares decimals and abbreviations
    def test_footnote_pattern_spares_decimals_and_abbreviations(self):
        cleaner = MarkdownCleaner(options=_only(remove_footnotes_in_text=True))
        for text in ["The value of pi is 3.14 and the version is 2.0 here.",
                     "Figure 3 shows version 3.5 of the model.",
                     "Eq. 2 shows that the effect is stable.",
                     "Fig. 2 presents the data."]:
            self.assertEqual(cleaner.clean_markdown_string(text), text)

    def test_footnote_pattern_still_removes_markers(self):
        cleaner = MarkdownCleaner(options=_only(remove_footnotes_in_text=True))
        self.assertNotIn(".12", cleaner.clean_markdown_string("A claim.12 The next one."))
        self.assertNotIn(".7", cleaner.clean_markdown_string("Last sentence of the line.7\nNext line."))

    # A4: \footnote{...} is removed without inventing a sentence break
    def test_latex_footnote_removed_without_period(self):
        text = "The result\\footnote{See appendix.} holds for every specification."
        self.assertEqual(self.cleaner._replace_within_lines(
            self.cleaner._replace_within_lines(text, self.cleaner.patterns.footnote_patterns, '. '),
            self.cleaner.patterns.bad_inline_patterns, ''),
            "The result holds for every specification.")

    # A5: line joining
    def test_crimp_keeps_em_and_en_dashes(self):
        result = self.cleaner._crimp_linebreaks("He paused for a long time—\nand then he left the room. Done.")
        self.assertEqual(result, "He paused for a long time—and then he left the room. Done.")

    def test_crimp_does_not_join_across_three_blank_lines(self):
        text = "hyphen-\n\n\n\ncontinued here. Yes."
        self.assertEqual(self.cleaner._crimp_linebreaks(text), text)
        self.assertEqual(self.cleaner._crimp_linebreaks("hyphen-\n\n\ncontinued here. Yes."),
                         "hyphencontinued here. Yes.")

    def test_crimp_does_not_join_thematic_break(self):
        text = "---\nSome text goes here. More text."
        self.assertEqual(self.cleaner._crimp_linebreaks(text), text)

    def test_crimp_leaves_code_fences_alone(self):
        line = "a" * 80
        text = "```\n    " + line + "\n    " + line + "\n```"
        self.assertEqual(self.cleaner._crimp_linebreaks(text), text)

    # A6: space collapsing leaves code blocks alone
    def test_space_collapse_skips_code_fences(self):
        cleaner = MarkdownCleaner(options=_only())
        text = "Some  text\n```\n        indented  code\n```"
        self.assertEqual(cleaner.clean_markdown_string(text), "Some text\n```\n        indented  code\n```")

    # A7, A8, A9: default line patterns
    def test_line_patterns_keep_ordinary_prose(self):
        lines = ["This was an important moment for the democratic 1960s movement as described.",
                 "the results of the experiment show that participants in the treatment group"]
        for line in lines:
            self.assertEqual(self.cleaner._remove_whole_lines(line, self.cleaner.patterns.bad_lines_patterns), line)

    def test_line_patterns_still_remove_targets(self):
        for line in ["c 2020 Elsevier", "INTRODUCTION AND OVERVIEW", "Contact: someone@example.org",
                     "The author(s) received no financial support for this work."]:
            self.assertEqual(self.cleaner._remove_whole_lines(line, self.cleaner.patterns.bad_lines_patterns), "")

    def test_acm_reference_format_section_removed(self):
        text = "## ACM Reference Format\nSome citation text\n## Next\nkept"
        acm = next(p for p in self.cleaner.patterns.sections_to_remove if p.startswith("ACM"))
        result = self.cleaner._remove_sections(text, acm)
        self.assertNotIn("Some citation text", result)

    # A10: closed ATX headings
    def test_closed_atx_heading_matches_section_pattern(self):
        result = self.cleaner._remove_sections("## References ##\nA ref\n## Next", r"References\s?\.?$")
        self.assertEqual(result, "## Next")

    # A11: inline parentheticals need a whole keyword
    def test_inline_patterns_need_whole_keyword(self):
        text = "The change (seemingly small) persisted (tableau one) here."
        self.assertEqual(self.cleaner._replace_within_lines(text, self.cleaner.patterns.bad_inline_patterns, ''), text)
        self.assertEqual(self.cleaner._replace_within_lines("Works (see above) well.",
                                                            self.cleaner.patterns.bad_inline_patterns, ''),
                         "Works  well.")

    # A12: loader and API robustness
    def test_remove_whole_lines_accepts_string_pattern(self):
        self.assertEqual(self.cleaner._remove_whole_lines("keep\nbad line\nkeep", r"bad"), "keep\nkeep")

    def test_default_patterns_are_not_shared(self):
        first = get_default_patterns()
        saved = list(first.bad_lines_patterns)
        first.bad_lines_patterns.clear()
        try:
            self.assertTrue(get_default_patterns().bad_lines_patterns)
        finally:
            first.bad_lines_patterns[:] = saved

    # A13, A14: quote normalization
    def test_quote_normalization(self):
        cleaner = MarkdownCleaner(options=_only(normalize_quotation_symbols=True))
        result = cleaner.clean_markdown_string("“Hello,” she said, ‘it’s `code`.’")
        self.assertEqual(result, "\"Hello,\" she said, 'it's `code`.'")

    # Round-2 review follow-ups
    def test_inline_patterns_remove_digit_attached_keyword(self):
        text = "Results improve (Figure2 shows this) in all cases."
        self.assertEqual(self.cleaner._replace_within_lines(text, self.cleaner.patterns.bad_inline_patterns, ''),
                         "Results improve  in all cases.")

    def test_crimp_joins_dash_after_digit(self):
        result = self.cleaner._crimp_linebreaks("prices from $10–\ntwenty dollars per unit were charged. Yes.")
        self.assertEqual(result, "prices from $10–twenty dollars per unit were charged. Yes.")

    def test_whole_line_removal_skips_code_fences(self):
        text = "```bash\npip install https://github.com/org/repo.git\n```"
        self.assertEqual(self.cleaner._remove_whole_lines(text, self.cleaner.patterns.bad_lines_patterns), text)

    def test_footnote_pattern_spares_abbreviation_before_number(self):
        cleaner = MarkdownCleaner(options=_only(remove_footnotes_in_text=True))
        for text in ["The construction appears in Ref. 12 Theorem 2.", "As shown on p. 42 The proof ends.",
                     "Treatment arm No. 5 The results differ."]:
            self.assertEqual(cleaner.clean_markdown_string(text), text)

    def test_duplicate_headlines_ignore_closing_sequence(self):
        result = self.cleaner._remove_duplicate_headlines("## Notes ##\ntext\n## Notes\nmore text", 1)
        self.assertEqual(result, "text\nmore text")

    def test_four_space_indented_fence_is_not_a_fence(self):
        text = "    ```\n# References\nref\n    ```\n# Next\nkept"
        self.assertNotIn("ref", self.cleaner._remove_sections(text, "References"))

    def test_loader_rejects_falsy_non_list(self):
        from markdowncleaner.config.loader import CleaningPatterns
        path = Path(tempfile.mkdtemp()) / "c.yaml"
        path.write_text('bad_lines_patterns: ""\n', encoding="utf-8")
        with self.assertRaises(TypeError):
            CleaningPatterns.from_yaml(path)
        path.write_text("bad_lines_patterns:\n", encoding="utf-8")
        self.assertEqual(CleaningPatterns.from_yaml(path).bad_lines_patterns, [])


if __name__ == '__main__':
    unittest.main()
