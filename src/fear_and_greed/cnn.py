#! /usr/bin/env python3

import datetime
import typing
import requests
from random import choice
import csv
import io
import requests

URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

USER_AGENTS = [
    # Chrome on Windows 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    # Firefox on Macos
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:100.0) Gecko/20100101 Firefox/100.0",
]


class FearGreedIndex(typing.NamedTuple):
    value: float
    description: str
    last_update: datetime.datetime


class Fetcher:
    """Fetcher gets the HTML contents of CNN's Fear & Greed Index website."""

    def __call__(self) -> dict:
        user_agent = choice(USER_AGENTS)
        headers = {
            "User-Agent": user_agent,
        }
        r = requests.get(URL, headers=headers)
        r.raise_for_status()
        return r.json()


def get(fetcher: typing.Optional[Fetcher] = None) -> FearGreedIndex:
    """Returns CNN's Fear & Greed Index."""

    if fetcher is None:
        fetcher = Fetcher()

    response = fetcher()["fear_and_greed"]
    return FearGreedIndex(
        value=response["score"],
        description=response["rating"],
        last_update=datetime.datetime.fromisoformat(response["timestamp"]),
    )

def historical(fetcher: typing.Optional[Fetcher] = None, start_date: typing.Optional[datetime.datetime] = None, end_date: typing.Optional[datetime.datetime] = None) -> typing.List[FearGreedIndex]:
    """Returns CNN's Fear & Greed Index historical data."""
    global URL

    if fetcher is None:
        fetcher = Fetcher()

    fear_greed_historical = []
    cnn_cutoff_date = datetime.datetime(2021, 2, 1, tzinfo=datetime.timezone.utc)

    URL = URL.split("/graphdata")[0] + "/graphdata"
    if start_date is not None:
        if start_date < cnn_cutoff_date:
            backup_data = "https://raw.githubusercontent.com/Chanda-Holdings/fear-greed-data/main/fear-greed-2011-2023.csv"
        
            csv_response = requests.get(backup_data)
            csv_response.raise_for_status()
            
            # Convert the response content to a file-like object
            csv_file = io.StringIO(csv_response.text)
            
            # Read the CSV data
            csv_reader = csv.DictReader(csv_file)
            
            # Convert CSV data to FearGreedIndex objects
            for row in csv_reader:
                date = datetime.datetime.strptime(row['Date'], '%m/%d/%Y').replace(tzinfo=datetime.timezone.utc)
                if date >= cnn_cutoff_date or date < start_date:
                    continue
                
                fear_greed_historical.append(FearGreedIndex(
                    value=float(row['Fear Greed']),
                    description="",
                    # description=row['description'],
                    last_update=date
                ))
            
            start_date = cnn_cutoff_date

        URL = URL + "/" + start_date.strftime("%Y-%m-%d")

    response = fetcher().get("fear_and_greed_historical", {})
    
    if "data" not in response:
        raise ValueError("No historical data found")

    historical_data = response["data"]
    for data in historical_data:
        if end_date is not None and datetime.datetime.fromtimestamp(data["x"] / 1000, tz=datetime.timezone.utc) > end_date:
            continue
        
        fear_greed_historical.append(FearGreedIndex(
            value=data["y"],
            description=data["rating"],
            last_update=datetime.datetime.fromtimestamp(data["x"] / 1000, tz=datetime.timezone.utc),
        ))
        
    fear_greed_historical.sort(key=lambda x: x.last_update)
    
    return fear_greed_historical
        
