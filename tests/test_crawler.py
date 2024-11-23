import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.crawler.crawler import PageContent, _clean_url, _link_has_extension, _extract_page, _crawl_page, crawl_site

class TestPageContent(unittest.TestCase):
    def test_construct_text(self):
        page_content = PageContent(
            divs=["div 1", "div 2"],
            paragraphs=["paragraph 1", "paragraph 2"],
            headings=["Heading 1", "Heading 2"],
            lists=["Item 1", "Item 2"],
            url="http://example.com",
            links=["http://example.com/link1", "http://example.com/link2"]
        )

        expected_output = """URL:
http://example.com

Headings:
1. Heading 1
2. Heading 2

Paragraphs:
paragraph 1
paragraph 2

Divs:
div 1
div 2

Lists:
Item 1
Item 2

Links:
- http://example.com/link1
- http://example.com/link2
"""

        self.assertEqual(page_content.construct_text(), expected_output)

class TestCrawler(unittest.IsolatedAsyncioTestCase):

    @patch("httpx.AsyncClient.get")
    async def test_extract_very_small_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><p>Test paragraph</p></body></html>"
        mock_get.return_value = mock_response

        page_content = await _extract_page("http://example.com")

        self.assertEqual(len(page_content.paragraphs()), 1)
        self.assertEqual(page_content.paragraphs()[0], "Test paragraph")

    @patch("httpx.AsyncClient.get")
    async def test_extract_small_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Main Heading</h1>
                    <p>Paragraph 1</p>
                    <p>Paragraph 2 with more <a href="http://example.com/link">details</a></p>
                    <ul>
                        <li>List item 1</li>
                        <li>List item 2</li>
                    </ul>
                    <div>Some div content</div>
                </body>
            </html>
        """
        mock_get.return_value = mock_response

        page_content = await _extract_page("http://example.com")

        paragraphs = page_content.paragraphs()
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0], "Paragraph 1")
        self.assertEqual(paragraphs[1], "Paragraph 2 with more details")

        headings = page_content.headings()
        self.assertEqual(len(headings), 1)
        self.assertEqual(headings[0], "Main Heading")

        links = page_content.links()
        self.assertIn("http://example.com/link", links)

        lists = page_content.lists()
        self.assertEqual(len(lists), 2)
        self.assertEqual(lists[0], "List item 1")
        self.assertEqual(lists[1], "List item 2")

        divs = page_content.divs()
        self.assertEqual(len(divs), 1)
        self.assertEqual(divs[0], "Some div content")
