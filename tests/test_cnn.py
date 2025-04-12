#! /usr/bin/env python3

import datetime
import json
import pathlib
import zoneinfo

from absl.testing import absltest
from fear_and_greed import cnn

FAKE_JSON_RESPONSE_GOLDEN_FILE = (
    pathlib.Path(__file__).parent / "response-golden.json"
).resolve()


class FetchFearGreedIndexTest(absltest.TestCase):
    def test_get(self):
        with open(FAKE_JSON_RESPONSE_GOLDEN_FILE, "rt") as fd:
            # Lambda is evaluated lazily, force JSON load while file is open.
            content = json.load(fd)
            fake_fetcher = lambda: content
        got = cnn.get(fetcher=fake_fetcher)

        want = cnn.FearGreedIndex(
            30.8254,
            "fear",
            datetime.datetime(
                year=2022,
                month=4,
                day=25,
                hour=16,
                minute=21,
                second=9,
                microsecond=254000,
                tzinfo=zoneinfo.ZoneInfo("UTC"),
            ),
        )
        self.assertEqual(got, want)

    def test_historical(self):
        with open(FAKE_JSON_RESPONSE_GOLDEN_FILE, "rt") as fd:
            # Lambda is evaluated lazily, force JSON load while file is open.
            content = json.load(fd)
            fake_fetcher = lambda: content
        got = cnn.historical(fetcher=fake_fetcher)

        self.assertEqual(len(got), 269)
        
        first_five = [
            cnn.FearGreedIndex(51.03333333333334, "neutral", datetime.datetime.fromtimestamp(1619395200.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(52.79999999999999, "neutral", datetime.datetime.fromtimestamp(1619481600.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(54.133333333333326, "neutral", datetime.datetime.fromtimestamp(1619568000.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(58.93333333333334, "greed", datetime.datetime.fromtimestamp(1619654400.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(49.26666666666667, "neutral", datetime.datetime.fromtimestamp(1619740800.0, tz=datetime.timezone.utc))
        ]
        
        self.assertEqual(got[:5], first_five)

        last_five = [
            cnn.FearGreedIndex(41.1246, "fear", datetime.datetime.fromtimestamp(1650585600.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(40.1512, "fear", datetime.datetime.fromtimestamp(1650672000.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(40.1512, "fear", datetime.datetime.fromtimestamp(1650758400.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(30.8254, "fear", datetime.datetime.fromtimestamp(1650844800.0, tz=datetime.timezone.utc)),
            cnn.FearGreedIndex(30.8254, "fear", datetime.datetime.fromtimestamp(1650903669.254, tz=datetime.timezone.utc))
        ]

        self.assertEqual(got[-5:], last_five)

    def test_historical_with_start_date(self):
        got = cnn.historical(start_date=datetime.datetime(2021, 4, 26, tzinfo=datetime.timezone.utc))
        
        self.assertEqual(got[0].last_update, datetime.datetime(2021, 4, 26, 0, 0, 0, 0, tzinfo=datetime.timezone.utc))
        
    def test_historical_with_end_date_distant(self):
        got = cnn.historical(end_date=datetime.datetime(2021, 4, 26, tzinfo=datetime.timezone.utc))
        
        self.assertEqual(len(got), 0)
    
    def test_historical_with_end_date(self):
        today = datetime.datetime.now(datetime.timezone.utc)
        closest_weekday = (today - datetime.timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        got = cnn.historical(end_date=closest_weekday)
        assert len(got) > 0

        self.assertEqual(got[-1].last_update, closest_weekday)

    def test_historical_with_start_and_end_date(self):
        start_date = datetime.datetime(2021, 4, 26, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(2023, 8, 10, tzinfo=datetime.timezone.utc)
        got = cnn.historical(start_date=start_date, end_date=end_date)
        
        assert len(got) > 0
        
        self.assertEqual(got[0].last_update, start_date)
        self.assertEqual(got[-1].last_update, end_date)
        


        
        

        
        
        
        
        

if __name__ == "__main__":
    absltest.main()
