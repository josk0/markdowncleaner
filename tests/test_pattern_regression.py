"""
Regression tests for default_cleaning_patterns.yaml

These tests ensure that refactoring or consolidating regex patterns
does not change the cleaning behavior. Each test targets specific
pattern categories from the YAML configuration.

Run with: python -m pytest tests/test_pattern_regression.py -v
"""

import unittest
from markdowncleaner.markdowncleaner import MarkdownCleaner, CleanerOptions
from markdowncleaner.config.loader import get_default_patterns


class TestSectionsToRemove(unittest.TestCase):
    """Tests for sections_to_remove patterns."""

    def setUp(self):
        # Disable other cleaning to isolate section removal
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_whole_lines = False
        options.remove_within_lines = False
        options.remove_footnotes_in_text = False
        options.replace_within_lines = False
        options.crimp_linebreaks = False
        options.remove_references_heuristically = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_removes_references_section(self):
        text = "# Introduction\nContent here.\n\n# References\n1. Citation one.\n2. Citation two."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("# Introduction", result)
        self.assertNotIn("# References", result)
        self.assertNotIn("Citation one", result)

    def test_removes_references_with_period(self):
        text = "# Content\nText.\n\n# References.\nRef content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# References.", result)

    def test_removes_numbered_references(self):
        text = "# Content\nText.\n\n# 7. References\nRef content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("References", result)

    def test_removes_bibliography_section(self):
        text = "# Main\nContent.\n\n# Bibliography\nEntries here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Bibliography", result)

    def test_removes_acknowledgements_section(self):
        text = "# Paper\nContent.\n\n# Acknowledgements\nThanks to everyone."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Acknowledgements", result)

    def test_removes_acknowledgments_american_spelling(self):
        text = "# Paper\nContent.\n\n# Acknowledgments\nThanks."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Acknowledgments", result)

    def test_removes_funding_section(self):
        text = "# Study\nContent.\n\n# Funding\nGrant details."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Funding", result)

    def test_removes_endnotes_section(self):
        text = "# Article\nContent.\n\n# Endnotes\n1. Note one."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Endnotes", result)

    def test_removes_works_cited_section(self):
        text = "# Essay\nContent.\n\n# Works Cited\nAuthor, Title."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Works Cited", result)

    def test_removes_notes_section(self):
        text = "# Article\nContent.\n\n# Notes\nNote content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Notes", result)

    def test_removes_keywords_section(self):
        text = "# Abstract\nContent.\n\n# Keywords\nword1, word2"
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Keywords", result)

    def test_removes_author_biographies(self):
        text = "# Conclusion\nContent.\n\n# Author Biographies\nJohn Doe is..."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Author Biographies", result)

    def test_removes_about_the_author(self):
        text = "# End\nContent.\n\n# About the author\nBio here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# About the author", result)

    def test_removes_table_of_contents(self):
        text = "# Book\n\n# Table of Contents\n1. Chapter 1\n\n# Chapter 1\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Table of Contents", result)
        self.assertIn("# Chapter 1", result)

    def test_removes_declaration_competing_interest(self):
        text = "# Results\nData.\n\n# Declaration of Competing Interest\nNone."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Declaration of Competing Interest", result)

    def test_removes_compliance_ethical_standards(self):
        text = "# Methods\nDetails.\n\n# Compliance with Ethical Standards\nApproved."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Compliance with Ethical Standards", result)

    def test_removes_corresponding_author(self):
        text = "# Paper\nContent.\n\n# Corresponding author\nEmail here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Corresponding author", result)

    def test_removes_disclosure_statement(self):
        text = "# Study\nContent.\n\n# Disclosure statement\nNo conflicts."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("# Disclosure statement", result)

    def test_removes_authors_note(self):
        # Section removal handles this via sections_to_remove patterns
        text = "# Paper\nContent.\n\n# Authors Note\nNote here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Authors Note", result)


class TestBadLinesPatterns(unittest.TestCase):
    """Tests for bad_lines_patterns - entire lines that should be removed."""

    def setUp(self):
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_sections = False
        options.remove_within_lines = False
        options.remove_footnotes_in_text = False
        options.replace_within_lines = False
        options.crimp_linebreaks = False
        options.remove_references_heuristically = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_removes_copyright_all_rights_reserved(self):
        text = "Content here.\nAll rights reserved.\nMore content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("All rights reserved", result)

    def test_removes_copyright_line(self):
        text = "Content.\nCopyright 2023 by Author Name.\nMore content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Copyright 2023", result)

    def test_removes_doi_lines(self):
        text = "Title.\ndoi: 10.1234/example.123\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("doi:", result)

    def test_removes_doi_url_format(self):
        text = "Reference.\n10.1234/journal.pone.0123456\nNext line."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("10.1234/journal", result)

    def test_removes_email_addresses(self):
        text = "Contact info.\nauthor@university.edu\nMore text."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("author@university.edu", result)

    def test_removes_urls(self):
        text = "See website.\nhttps://example.com/path/to/resource\nContinued."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("https://example.com", result)

    def test_removes_http_urls(self):
        text = "Link.\nhttp://example.org/page\nText."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("http://example.org", result)

    def test_removes_issn(self):
        text = "Journal info.\nISSN 1234-5678\nArticle."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("ISSN", result)

    def test_removes_isbn(self):
        text = "Book info.\nISBN 978-0-123456-78-9\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("ISBN", result)

    def test_removes_arxiv(self):
        text = "Preprint.\narxiv: 2301.12345\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("arxiv:", result)

    def test_removes_jstor(self):
        text = "Source.\nJSTOR stable/12345\nText."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("JSTOR", result)

    def test_removes_received_accepted_line(self):
        text = "Abstract.\nReceived 1 Jan 2023; accepted 15 Feb 2023\nIntro."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Received", result)

    def test_removes_received_line(self):
        text = "Title.\nReceived: January 1, 2023\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Received:", result)

    def test_removes_keywords_line(self):
        text = "Abstract.\nKeywords: machine learning, AI\nIntroduction."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Keywords:", result)

    def test_removes_key_words_line(self):
        text = "Abstract.\nKey words: neural networks\nIntro."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Key words:", result)

    def test_removes_conflict_of_interest(self):
        text = "Discussion.\nConflict of Interest: None declared.\nConclusion."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Conflict of Interest", result)

    def test_removes_open_access_line(self):
        text = "Article.\nOpen Access article under CC license.\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Open Access", result)

    def test_removes_department_of_line(self):
        text = "Authors.\nDepartment of Computer Science, University.\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Department of", result)

    def test_removes_copyright_symbol(self):
        text = "Footer.\n© 2023 Publisher Name\nNext page."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("©", result)

    def test_removes_registered_trademark(self):
        text = "Product.\nBrandName® Software\nFeatures."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("®", result)

    def test_removes_figure_caption_lines(self):
        text = "Content.\nFig. 1 Description of figure.\nMore text."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Fig.", result)

    def test_removes_figure_numbered(self):
        text = "Text.\nFigure 1: Caption here.\nContinued."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Figure 1:", result)

    def test_removes_table_caption_lines(self):
        text = "Data.\nTable 1: Results summary.\nDiscussion."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Table 1:", result)

    def test_removes_first_published_line(self):
        text = "Article.\nFirst published online: Jan 2023\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("First published", result)

    def test_removes_published_online_line(self):
        text = "Paper.\nPublished online: 2023-01-15\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Published online:", result)

    def test_removes_correspondence_line(self):
        text = "Authors.\nCorrespondence: author@email.com\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Correspondence:", result)

    def test_removes_unicode_footnote_lines(self):
        text = "Content.\n¹ This is a footnote.\nMore content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("¹ This is a footnote", result)

    def test_removes_latex_superscript_footnote(self):
        text = "Text.\n\\textsuperscript{1} Footnote text.\nMore."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("\\textsuperscript{1}", result)

    def test_removes_ibid_footnotes(self):
        text = "Content.\n5 Ibid., p. 123.\nMore content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Ibid.", result)

    def test_removes_see_note_lines(self):
        text = "Reference.\n12. See note 5 above.\nContinued."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("See note", result)

    def test_removes_supra_note_lines(self):
        text = "Citation.\n23 Author, supra note 15.\nText."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("supra note", result)

    def test_removes_all_caps_lines(self):
        text = "Content.\nCHAPTER ONE\nThe story begins."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("CHAPTER ONE", result)

    def test_removes_html_comments(self):
        text = "Content.\n<!-- This is a comment -->\nMore content."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("<!--", result)

    def test_removes_nsf_grant_lines(self):
        text = "Funding.\nNational Science Foundation (NSF) Grant No. 1234567\nResearch."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("NSF", result)

    def test_removes_grant_number_lines(self):
        text = "Support.\nGrant Number 123456789\nMethods."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Grant Number", result)

    def test_removes_dagger_lines(self):
        text = "Authors.\n† Equal contribution\nAbstract."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("†", result)

    def test_removes_double_dagger_lines(self):
        text = "Info.\n‡ Corresponding author\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("‡", result)

    def test_removes_thanks_lines(self):
        text = "Paper.\nWe thank the reviewers for helpful comments.\nIntro."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("thank the reviewers", result)

    def test_removes_grateful_lines(self):
        text = "Content.\nI am grateful for feedback from participants.\nMore."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("grateful for feedback", result)

    def test_removes_this_content_downloaded(self):
        text = "Article.\nThis content downloaded from 192.168.1.1\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("This content downloaded", result)

    def test_removes_creative_commons_line(self):
        text = "License.\nopen access article under the terms of the Creative Commons\nText."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Creative Commons", result)

    def test_removes_author_contributions_line(self):
        text = "Methods.\n** Author contributions: AB designed study.\nResults."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Author contributions", result)

    def test_removes_views_expressed_line(self):
        text = "Disclaimer.\nThe views expressed in this article are...\nContent."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("views expressed in this", result)

    def test_removes_competing_interests_line(self):
        text = "Declarations.\nCompeting interests: None.\nReferences."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("Competing interests", result)

    def test_removes_us_zip_code_lines(self):
        text = "Address.\nBoston, MA 02115, USA\nContact."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("MA 02115", result)


class TestBadInlinePatterns(unittest.TestCase):
    """Tests for bad_inline_patterns - patterns removed from within lines."""

    def setUp(self):
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_sections = False
        options.remove_whole_lines = False
        options.remove_footnotes_in_text = False
        options.replace_within_lines = False
        options.crimp_linebreaks = False
        options.remove_references_heuristically = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_removes_single_citation(self):
        text = "This finding [1] is important."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("[1]", result)
        self.assertIn("This finding", result)
        self.assertIn("is important", result)

    def test_removes_multiple_citations(self):
        text = "Studies show [1, 2, 3] that this works."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("[1, 2, 3]", result)

    def test_removes_citation_range(self):
        text = "Research [12, 15, 23] confirms this."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("[12, 15, 23]", result)

    def test_removes_see_parenthetical(self):
        text = "The method (see above) works well."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(see above)", result)

    def test_removes_see_section_reference(self):
        text = "Details (see Section 3.2) are provided."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(see Section 3.2)", result)

    def test_removes_figure_reference(self):
        text = "The results (Figure 1) show improvement."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(Figure 1)", result)

    def test_removes_table_reference(self):
        text = "Data (Table 2) summarizes findings."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(Table 2)", result)

    def test_removes_section_reference(self):
        text = "As discussed (Section 4) previously."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(Section 4)", result)

    def test_removes_chapter_reference(self):
        text = "See (Chapter 5) for details."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(Chapter 5)", result)

    def test_removes_page_reference(self):
        text = "The quote (p.123) states this."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(p.123)", result)

    def test_removes_page_reference_with_period(self):
        text = "Found on (p123) of the book."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("(p123)", result)

    def test_removes_latex_footnote(self):
        text = "Important point\\footnote{See appendix} here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("\\footnote", result)

    def test_removes_trailing_ellipsis_at_end_of_string(self):
        # Note: Pattern uses $ which matches end of STRING, not end of line (no MULTILINE flag)
        text = "The sentence continues..."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("...", result)


class TestFootnotePatterns(unittest.TestCase):
    """Tests for footnote_patterns - replaced with '. '"""

    def setUp(self):
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_sections = False
        options.remove_whole_lines = False
        options.remove_within_lines = False
        options.replace_within_lines = False
        options.crimp_linebreaks = False
        options.remove_references_heuristically = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_removes_single_digit_footnote(self):
        text = "This is a sentence.1 More text follows."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn(".1 ", result)
        self.assertIn(". ", result)

    def test_removes_double_digit_footnote(self):
        text = "Important finding.23 The research shows."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn(".23", result)

    def test_removes_footnote_with_space(self):
        text = "End of sentence. 5 Next sentence begins."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn(". 5 ", result)

    def test_removes_multiple_footnotes(self):
        text = "First point.1, 2, 3 Supporting evidence."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn(".1, 2, 3", result)

    def test_removes_unicode_superscript_footnote(self):
        text = "The claim.¹²³ Evidence follows."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn(".¹²³", result)

    def test_removes_latex_textsuperscript_footnote(self):
        text = "Statement.\\textsuperscript{4} Continuation."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("\\textsuperscript{4}", result)

    def test_removes_latex_math_superscript(self):
        text = "Assertion.\\(^{5}\\) More text."
        result = self.cleaner.clean_markdown_string(text)
        self.assertNotIn("\\(^{5}\\)", result)


class TestReplacements(unittest.TestCase):
    """Tests for replacements dict - character substitutions."""

    def setUp(self):
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_sections = False
        options.remove_whole_lines = False
        options.remove_within_lines = False
        options.remove_footnotes_in_text = False
        options.crimp_linebreaks = False
        options.remove_references_heuristically = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_replaces_glyph_28_fi(self):
        text = "The GLYPH<28>rst example."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("first", result)
        self.assertNotIn("GLYPH<28>", result)

    def test_replaces_glyph_28_escaped_fi(self):
        text = "The GLYPH&lt;28&gt;rst item."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("first", result)

    def test_replaces_glyph_29_fl(self):
        text = "The GLYPH<29>ow of water."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("flow", result)

    def test_replaces_glyph_29_escaped_fl(self):
        text = "A GLYPH&lt;29&gt;ower blooms."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("flower", result)

    def test_replaces_unifb01_fi(self):
        text = "The /uniFB01rst test."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("first", result)

    def test_replaces_unifb02_fl(self):
        text = "Water /uniFB02ows down."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("flows", result)

    def test_replaces_unifb00_ff(self):
        text = "The e/uniFB00ect is clear."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("effect", result)

    def test_replaces_unifb03_ffi(self):
        text = "An e/uniFB03cient method."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("efficient", result)

    def test_replaces_glyph_21_dash(self):
        text = "WordGLYPH<21>break here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("Word-break", result)

    def test_replaces_glyph_22_emdash(self):
        text = "FirstGLYPH<22>second part."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("—", result)

    def test_replaces_html_ampersand(self):
        text = "Research &amp; Development."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("Research & Development", result)

    def test_replaces_latex_item(self):
        text = "\\item First point in list."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("- First point", result)


class TestBibliographyScorer(unittest.TestCase):
    """Tests for _score_bibliography_line and _remove_bibliographic_lines."""

    def setUp(self):
        options = CleanerOptions()
        options.remove_short_lines = False
        options.remove_sections = False
        options.remove_whole_lines = False
        options.remove_within_lines = False
        options.remove_footnotes_in_text = False
        options.replace_within_lines = False
        options.crimp_linebreaks = False
        self.cleaner = MarkdownCleaner(options=options)

    def test_scores_year_in_parentheses(self):
        score = self.cleaner._score_bibliography_line("Author, A. (2023). Title of paper.")
        self.assertGreater(score, 0)

    def test_scores_year_in_brackets(self):
        score = self.cleaner._score_bibliography_line("Author, A. [1999]. Historical work.")
        self.assertGreater(score, 0)

    def test_scores_page_ranges(self):
        score = self.cleaner._score_bibliography_line("Journal Name, 15, pp. 123-456.")
        self.assertGreater(score, 0)

    def test_scores_volume_issue(self):
        score = self.cleaner._score_bibliography_line("Journal of Science, 42(3), 100-150.")
        self.assertGreaterEqual(score, 3)  # Volume/issue pattern is 3 points

    def test_scores_doi(self):
        score = self.cleaner._score_bibliography_line("Available at doi.org/10.1234/example")
        self.assertGreaterEqual(score, 3)

    def test_scores_doi_prefix(self):
        score = self.cleaner._score_bibliography_line("Reference with DOI: 10.1234/test")
        self.assertGreaterEqual(score, 3)

    def test_scores_et_al(self):
        score = self.cleaner._score_bibliography_line("Smith et al. (2020). Study findings.")
        self.assertGreater(score, 0)

    def test_scores_editor_markers(self):
        score = self.cleaner._score_bibliography_line("In: Smith, J. (Ed.). Handbook of Science.")
        self.assertGreaterEqual(score, 3)

    def test_scores_editors_plural(self):
        score = self.cleaner._score_bibliography_line("In: Smith & Jones (Eds.). Collection.")
        self.assertGreaterEqual(score, 3)

    def test_scores_ampersand(self):
        score = self.cleaner._score_bibliography_line("Smith, A. & Jones, B. (2021). Joint work.")
        self.assertGreater(score, 0)

    def test_scores_journal_keyword(self):
        score = self.cleaner._score_bibliography_line("Published in Journal of Applied Science.")
        self.assertGreaterEqual(score, 2)

    def test_scores_proceedings(self):
        score = self.cleaner._score_bibliography_line("In Proceedings of the Conference on AI.")
        self.assertGreaterEqual(score, 2)

    def test_scores_university_press(self):
        score = self.cleaner._score_bibliography_line("Cambridge: Cambridge University Press.")
        self.assertGreaterEqual(score, 2)

    def test_scores_numbered_reference(self):
        score = self.cleaner._score_bibliography_line("1. First reference in the list here.")
        self.assertGreater(score, 0)

    def test_scores_author_initials(self):
        score = self.cleaner._score_bibliography_line("Wiesner, J. B. (1965). Science and policy.")
        self.assertGreater(score, 0)

    def test_scores_publisher_location(self):
        score = self.cleaner._score_bibliography_line("New York: Academic Press, pp. 50-75.")
        self.assertGreater(score, 0)

    def test_does_not_score_short_lines(self):
        score = self.cleaner._score_bibliography_line("Short line.")
        self.assertEqual(score, 0)

    def test_does_not_score_regular_content(self):
        score = self.cleaner._score_bibliography_line("This is a regular paragraph of text that discusses findings in detail.")
        self.assertLess(score, 3)  # Should not reach removal threshold

    def test_removes_high_scoring_bibliography_line(self):
        text = "Introduction paragraph here.\n" \
               "Smith, A. & Jones, B. (2021). Title. Journal of Science, 42(3), 100-150.\n" \
               "Conclusion paragraph here."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("Introduction", result)
        self.assertIn("Conclusion", result)
        self.assertNotIn("Journal of Science", result)

    def test_keeps_regular_content(self):
        text = "This is a regular paragraph discussing research findings.\n" \
               "The study found significant results in the experiment."
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("regular paragraph", result)
        self.assertIn("significant results", result)


class TestIntegrationRegression(unittest.TestCase):
    """Integration tests with realistic document samples."""

    def setUp(self):
        self.cleaner = MarkdownCleaner()

    def test_academic_paper_cleaning(self):
        """Comprehensive test with realistic academic paper content."""
        sample = """# Machine Learning in Healthcare

## Abstract

This paper presents novel GLYPH<28>ndings in healthcare AI.1 Our research [1, 2] demonstrates
signiGLYPH<28>cant improvements (see Figure 1) in diagnostic accuracy.

Keywords: machine learning, healthcare, AI

## Introduction

The healthcare industry has seen remarkable advances.2 Previous work (Table 1) shows
promising results. Contact: researcher@university.edu

doi: 10.1234/example.healthcare.2023

## Methods

We developed an efGLYPH<28>cient algorithm for analysis. The method (Section 3.1) builds on
prior research [3, 4, 5].

Figure 1: System architecture overview.

## Results

Our GLYPH<28>ndings show 95% accuracy. The data (Figure 2) conGLYPH<28>rms our hypothesis.

Table 1: Performance metrics summary.

## Discussion

These results.3, 4 demonstrate the potential of AI in healthcare applications.

## Conclusion

We presented signiGLYPH<28>cant advances in healthcare AI diagnostics.

## Acknowledgements

We thank the reviewers for helpful comments and feedback.

## References

1. Smith, A. & Jones, B. (2020). Machine learning review. Journal of AI, 15(2), 100-150.
2. Brown, C. et al. (2021). Healthcare applications. Proceedings of ICML, pp. 500-510.

Copyright 2023 All rights reserved.
https://example.com/paper
"""

        result = self.cleaner.clean_markdown_string(sample)

        # Content should be preserved
        self.assertIn("# Machine Learning in Healthcare", result)
        self.assertIn("## Abstract", result)
        self.assertIn("## Introduction", result)
        self.assertIn("## Methods", result)
        self.assertIn("## Results", result)
        self.assertIn("## Discussion", result)
        self.assertIn("## Conclusion", result)

        # GLYPH replacements should be applied
        self.assertIn("findings", result)
        self.assertIn("significant", result)
        self.assertIn("efficient", result)
        self.assertIn("confirms", result)
        self.assertNotIn("GLYPH", result)

        # Citations should be removed
        self.assertNotIn("[1, 2]", result)
        self.assertNotIn("[3, 4, 5]", result)

        # Footnotes should be removed
        self.assertNotIn(".1 ", result)
        self.assertNotIn(".2 ", result)
        self.assertNotIn(".3, 4", result)

        # Inline references should be removed
        self.assertNotIn("(see Figure 1)", result)
        self.assertNotIn("(Table 1)", result)
        self.assertNotIn("(Section 3.1)", result)
        self.assertNotIn("(Figure 2)", result)

        # Bad lines should be removed
        self.assertNotIn("Keywords:", result)
        self.assertNotIn("researcher@university.edu", result)
        self.assertNotIn("doi:", result)
        self.assertNotIn("Figure 1:", result)
        self.assertNotIn("Table 1:", result)
        self.assertNotIn("Copyright", result)
        self.assertNotIn("https://", result)

        # Sections should be removed
        self.assertNotIn("## Acknowledgements", result)
        self.assertNotIn("thank the reviewers", result)
        self.assertNotIn("## References", result)
        self.assertNotIn("Smith, A. & Jones", result)

    def test_book_chapter_cleaning(self):
        """Test with book chapter content."""
        # Note: Avoid numbered sections like "5.1" - footnote pattern matches ".1"
        sample = """# Chapter Five: Ethics in AI

## Table of Contents

1. Introduction
2. Background

## Introduction

The ethical implications of artiGLYPH<28>cial intelligence are profound.1

First published online: January 2023

ISBN 978-0-123456-78-9

## Background

Previous research &amp; analysis (Chapter 3) established key principles.

Library of Congress Cataloging-in-Publication Data

## Author Biography

John Doe is a professor at Example University.

## Notes

1. See Smith (2020) for discussion.
"""

        result = self.cleaner.clean_markdown_string(sample)

        # Main content preserved
        self.assertIn("# Chapter Five: Ethics in AI", result)
        self.assertIn("## Introduction", result)
        self.assertIn("## Background", result)

        # Replacements applied
        self.assertIn("artificial", result)
        self.assertIn("& analysis", result)

        # Sections removed
        self.assertNotIn("## Table of Contents", result)
        self.assertNotIn("## Author Biography", result)
        self.assertNotIn("## Notes", result)

        # Bad lines removed
        self.assertNotIn("First published", result)
        self.assertNotIn("ISBN", result)
        self.assertNotIn("Library of Congress", result)

    def test_preserves_regular_content(self):
        """Ensure regular paragraphs are not incorrectly removed by pattern matching."""
        # Use cleaner with short line removal disabled to isolate pattern testing
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner = MarkdownCleaner(options=options)

        sample = """# Research Paper

## Introduction

This is a regular paragraph that should be preserved entirely. It contains normal academic writing without any special markers or citations that would trigger removal patterns.

The methodology section describes our approach in detail. We collected data from multiple sources and analyzed it using standard statistical methods.

## Results

Our analysis revealed several important findings. The primary outcome showed a statistically significant improvement in performance metrics.

## Conclusion

In conclusion, our research demonstrates the effectiveness of the proposed approach. Future work will explore additional applications.
"""

        result = cleaner.clean_markdown_string(sample)

        # All sections should be preserved
        self.assertIn("# Research Paper", result)
        self.assertIn("## Introduction", result)
        self.assertIn("## Results", result)
        self.assertIn("## Conclusion", result)

        # Content should be preserved
        self.assertIn("regular paragraph", result)
        self.assertIn("methodology section", result)
        self.assertIn("important findings", result)
        self.assertIn("Future work", result)


if __name__ == '__main__':
    unittest.main()
