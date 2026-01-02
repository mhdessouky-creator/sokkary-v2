import unittest
from unittest.mock import patch, MagicMock
from tools.fpl_tool import FPLTool

class TestFPLTool(unittest.TestCase):

    @patch('requests.get')
    def test_get_news_empty(self, mock_get):
        # Mock responses to raise exceptions or return empty to simulate no news
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Failed")
        mock_get.return_value = mock_response

        tool = FPLTool()
        # Suppress logging during test
        tool.logger.setLevel("CRITICAL")

        news = tool.get_news()
        self.assertIn("No news found", news)

    @patch('requests.get')
    def test_get_news_success(self, mock_get):
        # Setup a mock response for one of the sources
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><article><h2>Breaking Injury News</h2></article></html>'
        mock_response.json.return_value = {} # For json calls

        mock_get.return_value = mock_response

        tool = FPLTool()
        news = tool.get_news()

        # We expect "Breaking Injury News" to be in the output
        self.assertIn("Breaking Injury News", news)
        self.assertIn("Fantasy Football Scout", news) # Source name

if __name__ == '__main__':
    unittest.main()
