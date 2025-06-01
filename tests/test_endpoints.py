import datetime
import unittest
from unittest import skipIf
import os
import time
import requests
import zoneinfo
from fear_and_greed import cnn

#! /usr/bin/env python3


# Skip integration tests by default, run only when explicitly requested
SKIP_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS", "0") != "1"
SKIP_MESSAGE = "Integration tests skipped. Set RUN_INTEGRATION_TESTS=1 to run."


@skipIf(SKIP_INTEGRATION_TESTS, SKIP_MESSAGE)
class FearGreedLiveEndpointTests(unittest.TestCase):
    def setUp(self):
        # Add delay between tests to avoid rate limiting
        time.sleep(1)

    def test_live_get(self):
        """Test that the current fear and greed index can be fetched from live endpoint."""
        result = cnn.get()

        self.assertIsInstance(result, cnn.FearGreedIndex)
        self.assertIsInstance(result.value, float)
        self.assertIsInstance(result.description, str)
        self.assertIsInstance(result.last_update, datetime.datetime)

        # Value should be between 0 and 100
        self.assertGreaterEqual(result.value, 0)
        self.assertLessEqual(result.value, 100)

        # Description should be one of the expected values
        valid_descriptions = [
            "extreme fear",
            "fear",
            "neutral",
            "greed",
            "extreme greed",
        ]
        self.assertIn(result.description.lower(), valid_descriptions)

    def test_live_historical(self):
        """Test that historical data can be fetched from live endpoint."""
        result = cnn.historical()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # Check the first item
        self.assertIsInstance(result[0], cnn.FearGreedIndex)
        self.assertIsInstance(result[0].value, float)
        self.assertIsInstance(result[0].description, str)
        self.assertIsInstance(result[0].last_update, datetime.datetime)

    def test_live_historical_with_recent_start_date(self):
        """Test historical data with recent start date."""
        # Use a date that's likely to have data (3 months ago)
        # Normalize to start of day to match API behavior
        start_date = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=90)
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        result = cnn.historical(start_date=start_date)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # First date should be >= start_date (comparing dates only)
        self.assertGreaterEqual(result[0].last_update.date(), start_date.date())

    def test_live_historical_with_start_and_end_date(self):
        """Test historical data with start and end date constraints."""
        end_date = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - datetime.timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        result = cnn.historical(start_date=start_date, end_date=end_date)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # Data should be within date range (comparing dates only)
        self.assertGreaterEqual(result[0].last_update.date(), start_date.date())
        self.assertLessEqual(result[-1].last_update.date(), end_date.date())

    def test_live_historical_with_old_start_date(self):
        """Test historical data with a start date before CNN's cutoff."""
        old_start_date = datetime.datetime(2015, 1, 1, tzinfo=datetime.timezone.utc)
        result = cnn.historical(start_date=old_start_date)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # First date should be at or near the requested start date
        # Allow for a 1-day difference since historical data might not be available for every single day
        first_date = result[0].last_update.date()
        start_date = old_start_date.date()
        allowed_difference = datetime.timedelta(days=1)

        self.assertLessEqual(
            (first_date - start_date),
            allowed_difference,
            f"First date {first_date} is more than {allowed_difference} away from requested start date {start_date}",
        )

    def test_url_format_consistency(self):
        """Test that the URL format is as expected."""
        try:
            fetcher = cnn.Fetcher()
            response = fetcher()

            # Verify expected structure
            self.assertIn("fear_and_greed", response)
            fg_data = response["fear_and_greed"]

            self.assertIn("score", fg_data)
            self.assertIn("rating", fg_data)
            self.assertIn("timestamp", fg_data)

            # Test historical endpoint format
            historical_response = cnn.historical(
                start_date=datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=30)
            )
            self.assertGreater(len(historical_response), 0)

        except requests.RequestException as e:
            self.fail(f"Request failed, API may have changed: {e}")
        except (KeyError, ValueError) as e:
            self.fail(f"Response format has changed: {e}")


if __name__ == "__main__":
    unittest.main()
