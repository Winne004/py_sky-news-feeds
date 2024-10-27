import unittest
from unittest.mock import patch

from py_sky_rss_feeds import News, NewsCategory, FeedParser


class TestNews(unittest.TestCase):
    def setUp(self):
        """Initialize a News object before each test."""
        self.news = News()

    def test_available_categories(self):
        """Test that available_categories returns the correct list of category names."""
        expected_categories = [
            "HOME",
            "UK",
            "WORLD",
            "US",
            "BUSINESS",
            "POLITICS",
            "TECHNOLOGY",
            "ENTERTAINMENT",
            "STRANGE",
        ]
        self.assertListEqual(self.news.available_categories(), expected_categories)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_get_feed_all_categories(self, mock_parse):
        """Test get_feed with all available categories."""
        mock_parse.return_value = {
            "entries": [{"title": "Article", "link": "http://example.com"}]
        }
        for category in NewsCategory:
            result = self.news.get_feed(category)
            self.assertEqual(len(result.entries), 1)
            mock_parse.assert_called_with(self.news.base_url + category.value)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_get_feed_no_entries(self, mock_parse):
        """Test get_feed when the feed returns no entries."""
        mock_parse.return_value = {"entries": []}
        result = self.news.get_feed(NewsCategory.UK)
        self.assertEqual(len(result.entries), 0)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_get_feed_limit_exceeds_entries(self, mock_parse):
        """Test get_feed with limit greater than available entries."""
        mock_parse.return_value = {
            "entries": [
                {"title": "Article 1", "link": "http://example.com/1"},
                {"title": "Article 2", "link": "http://example.com/2"},
            ]
        }
        result = self.news.get_feed(NewsCategory.UK, limit=5)
        self.assertEqual(len(result.entries), 2)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_get_feed_limit_less_than_entries(self, mock_parse):
        """Test get_feed with limit greater than available entries."""
        mock_parse.return_value = {
            "entries": [
                {"title": "Article 1", "link": "http://example.com/1"},
                {"title": "Article 2", "link": "http://example.com/2"},
            ]
        }
        result = self.news.get_feed(NewsCategory.UK, limit=1)
        self.assertEqual(len(result.entries), 1)

    def test_get_feed_invalid_type(self):
        """Test get_feed with an invalid category."""
        with self.assertRaises(AttributeError):
            self.news.get_feed("INVALID_CATEGORY")

    @patch("py_sky_rss_feeds.feedparser.parse", side_effect=Exception("Parsing error"))
    def test_parse_exception_handling(self, mock_parse):
        """Test that parse handles exceptions and returns an empty list."""
        result = self.news.parse("/invalid_path.xml")
        self.assertEqual(result, [])

    @patch("py_sky_rss_feeds.feedparser.parse", side_effect=Exception("Parsing error"))
    @patch("py_sky_rss_feeds.logger.error")
    def test_parse_logs_exception(self, mock_logger, mock_parse):
        """Test that parse logs an error when an exception occurs."""
        self.news.parse("/invalid_path.xml")
        mock_logger.assert_called_once()
        args, _ = mock_logger.call_args
        self.assertIn("Error parsing feed", args[0])

    # Test 8: Test parse with limit=None
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_no_limit(self, mock_parse):
        """Test parse returns all entries when limit is None."""
        mock_parse.return_value = {
            "entries": [
                {"title": f"Article {i}", "link": f"http://example.com/{i}"}
                for i in range(5)
            ]
        }
        result = self.news.parse("/uk.xml")
        self.assertEqual(len(result.entries), 5)

    # Test 9: Test initialization of FeedParser
    def test_feedparser_initialization(self):
        """Test that FeedParser initializes with the correct base URL."""
        base_url = "http://example.com/rss"
        parser = FeedParser(base_url)
        self.assertEqual(parser.base_url, base_url)

    # Test 10: Test News inherits from FeedParser correctly
    def test_news_inheritance(self):
        """Test that News is a subclass of FeedParser."""
        self.assertTrue(issubclass(News, FeedParser))
        self.assertIsInstance(self.news, FeedParser)

    # Test 11: Test parse method constructs correct URL
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_constructs_correct_url(self, mock_parse):
        """Test that parse constructs the correct URL."""
        path = "/test.xml"
        self.news.parse(path)
        expected_url = self.news.base_url + path
        mock_parse.assert_called_with(expected_url)

    # Test 12: Test get_feed with non-enum category input
    def test_get_feed_non_enum_category(self):
        """Test get_feed with a non-Enum category input."""
        with self.assertRaises(AttributeError):
            self.news.get_feed("/uk.xml")

    # Test 14: Test parse with malformed XML
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_malformed_xml(self, mock_parse):
        """Test parse with malformed XML data."""
        mock_parse.return_value = {
            "entries": [],
            "bozo_exception": Exception("Malformed XML"),
        }
        result = self.news.parse("/uk.xml")
        self.assertEqual(len(result.entries), 0)

    # Test 15: Test parse when feed returns non-200 HTTP status
    @patch("py_sky_rss_feeds.feedparser.parse", side_effect=Exception("HTTP Error 404"))
    def test_parse_http_error(self, mock_parse):
        """Test parse when the feed URL returns a non-200 HTTP status code."""
        result = self.news.parse("/nonexistent.xml")
        self.assertEqual(result, [])

    # Test 16: Test large number of entries
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_large_number_of_entries(self, mock_parse):
        """Test parse with a large number of entries."""
        mock_parse.return_value = {
            "entries": [
                {"title": f"Article {i}", "link": f"http://example.com/{i}"}
                for i in range(1000)
            ]
        }
        result = self.news.parse("/uk.xml")
        self.assertEqual(len(result.entries), 1000)

    # Test 17: Test unicode and special characters in entries
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_unicode_entries(self, mock_parse):
        """Test parse with entries containing Unicode and special characters."""
        mock_parse.return_value = {
            "entries": [
                {"title": "Artículo con acentos", "link": "http://example.com/1"},
                {"title": "新闻标题", "link": "http://example.com/2"},
            ]
        }
        result = self.news.parse("/uk.xml")
        self.assertEqual(len(result.entries), 2)
        self.assertEqual(result.entries[0].title, "Artículo con acentos")
        self.assertEqual(result.entries[1].title, "新闻标题")

    # Test 18: Test parse with empty base URL
    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_empty_base_url(self, mock_parse):
        """Test parse when base_url is empty."""
        parser = FeedParser("")
        parser.parse("/uk.xml")
        mock_parse.assert_called_with("/uk.xml")

    # Test 19: Test logging of information messages
    @patch("py_sky_rss_feeds.feedparser.parse")
    @patch("py_sky_rss_feeds.logger.info")
    def test_parse_logs_info_message(self, mock_logger, mock_parse):
        """Test that parse logs an info message when fetching the feed."""
        self.news.parse("/uk.xml")
        mock_logger.assert_called_once()
        args, _ = mock_logger.call_args
        self.assertIn("Fetching feed from", args[0])

    def test_news_initialization(self):
        """Test that News initializes with the correct base URL."""
        expected_base_url = "https://feeds.skynews.com/feeds/rss"
        self.assertEqual(self.news.base_url, expected_base_url)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_get_feed_with_zero_limit(self, mock_parse):
        """Test get_feed with limit set to zero."""
        with self.assertRaises(ValueError):
            self.news.get_feed(NewsCategory.UK, limit=-1)

    def test_get_feed_with_negative_limit(self):
        """Test get_feed with a negative limit."""
        with self.assertRaises(ValueError):
            self.news.get_feed(NewsCategory.UK, limit=-1)

    @patch("py_sky_rss_feeds.feedparser.parse", return_value=None)
    def test_parse_none_return(self, mock_parse):
        """Test parse when feedparser.parse returns None."""
        result = self.news.parse("/uk.xml")
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()
