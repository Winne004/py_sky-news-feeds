import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from pydantic import ValidationError

from py_sky_rss_feeds import Entries, FeedParser, News, NewsCategory, FeedService


class TestNews(unittest.TestCase):
    def setUp(self):
        """Initialize a News object before each test."""
        self.news = News(parser=FeedParser())

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

    @patch("py_sky_rss_feeds.logger.error")  # Patch logger first
    @patch("py_sky_rss_feeds.feedparser.parse", side_effect=Exception("Parsing error"))
    def test_parse_logs_exception(self, mock_parse, mock_logger):
        """Test that parse logs an error when an exception occurs and raises it."""

        with self.assertRaises(Exception) as context:
            self.news.parse_feed("/invalid_path.xml")

        self.assertEqual(str(context.exception), "Parsing error")

        mock_logger.assert_called_once()

        args, _ = mock_logger.call_args
        self.assertIn("Unexpected error parsing feed", args[0])

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_no_limit(self, mock_parse):
        """Test parse returns all entries when limit is None."""
        mock_parse.return_value = {
            "entries": [
                {"title": f"Article {i}", "link": f"http://example.com/{i}"}
                for i in range(5)
            ]
        }
        result = self.news.parse_feed("/uk.xml")
        self.assertEqual(len(result.entries), 5)

    def test_feedparser_initialization(self):
        """Test that FeedParser initializes with the correct base URL."""
        base_url = "http://example.com/rss"
        parser = FeedService(base_url, parser=FeedParser())
        self.assertEqual(parser.base_url, base_url)

    def test_news_inheritance(self):
        """Test that News is a subclass of FeedParser."""
        self.assertTrue(issubclass(News, FeedService))
        self.assertIsInstance(self.news, FeedService)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_constructs_correct_url(self, mock_parse):
        """Test that parse constructs the correct URL."""
        path = "/test.xml"
        self.news.parse_feed(path)
        expected_url = self.news.base_url + path
        mock_parse.assert_called_with(expected_url)

    def test_get_feed_non_enum_category(self):
        """Test get_feed with a non-Enum category input."""
        with self.assertRaises(AttributeError):
            self.news.get_feed("/uk.xml")

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_malformed_xml(self, mock_parse):
        """Test parse with malformed XML data."""
        mock_parse.return_value = {
            "entries": [],
            "bozo_exception": Exception("Malformed XML"),
        }
        result = self.news.parse_feed("/uk.xml")
        self.assertEqual(len(result.entries), 0)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_http_error(
        self,
        mock_parse,
    ):
        """Test parse raises an HTTPError when the feed URL returns a non-200 status code."""
        mock_parse.side_effect = HTTPError(
            url="/nonexistent.xml", code=404, msg="Not Found", hdrs=None, fp=None
        )

        with self.assertRaises(HTTPError):
            self.news.parse_feed("/nonexistent.xml")

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_large_number_of_entries(self, mock_parse):
        """Test parse with a large number of entries."""
        mock_parse.return_value = {
            "entries": [
                {"title": f"Article {i}", "link": f"http://example.com/{i}"}
                for i in range(1000)
            ]
        }
        result = self.news.parse_feed("/uk.xml")
        self.assertEqual(len(result.entries), 1000)

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_unicode_entries(self, mock_parse):
        """Test parse with entries containing Unicode and special characters."""
        mock_parse.return_value = {
            "entries": [
                {"title": "Artículo con acentos", "link": "http://example.com/1"},
                {"title": "新闻标题", "link": "http://example.com/2"},
            ]
        }
        result = self.news.parse_feed("/uk.xml")
        self.assertEqual(len(result.entries), 2)
        self.assertEqual(result.entries[0].title, "Artículo con acentos")
        self.assertEqual(result.entries[1].title, "新闻标题")

    @patch("py_sky_rss_feeds.feedparser.parse")
    def test_parse_with_empty_base_url(self, mock_parse):
        """Test parse when base_url is empty."""
        with self.assertRaises(ValidationError):
            FeedService("", FeedParser())

    @patch("py_sky_rss_feeds.feedparser.parse")
    @patch("py_sky_rss_feeds.logger.info")
    def test_parse_logs_info_message(self, mock_logger, mock_parse):
        """Test that parse logs an info message when fetching the feed."""
        self.news.parse_feed("/uk.xml")
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
        result = self.news.parse_feed("/uk.xml")
        expected_result = Entries(entries=[])
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
