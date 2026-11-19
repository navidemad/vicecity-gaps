"""Tests for build.py. Run: python3 -m unittest test_build.py

The digest Markdown is pasted from public posts, so the renderer must never let
raw HTML or javascript: links reach the live page, and the YouTube coverage label
must keep driving the coloured badge creators scan for.
"""

import unittest

import build


class MarkdownRenderingTest(unittest.TestCase):
    def test_raw_html_from_posts_is_escaped(self):
        out = build.markdown_to_html("Question <script>alert(1)</script> here")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_javascript_links_are_dropped_but_http_links_kept(self):
        out = build.markdown_to_html("[bad](javascript:alert(1)) and [post](https://x.com/p/1)")
        self.assertNotIn("javascript:", out)
        self.assertIn('href="https://x.com/p/1"', out)

    def test_coverage_label_becomes_a_badge(self):
        md = "| Question | YouTube |\n| --- | --- |\n| Is there first-person mode? | Conflicting answers |\n"
        out = build.markdown_to_html(md)
        self.assertIn('class="status status-conflict"', out)
        # Mobile layout reads the column name from data-label.
        self.assertIn('data-label="YouTube"', out)

    def test_unknown_label_is_plain_text(self):
        md = "| Question | YouTube |\n| --- | --- |\n| Q | Something else |\n"
        self.assertNotIn("status-", build.markdown_to_html(md))

    def test_headings_start_below_page_sections(self):
        # The page already uses h1 and h2; digest headings must not compete with them.
        self.assertIn("<h3>Top</h3>", build.markdown_to_html("# Top"))


if __name__ == "__main__":
    unittest.main()
