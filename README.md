Python wrapper for CNN's [Fear & Greed Index](https://money.cnn.com/data/fear-and-greed/).

Fetches CNN's website, parses the index value and returns the data as a three-element tuple.

# Installation

```bash
pip install fear-and-greed
```

# Usage example
## Fetch Current Fear & Greed Index

```python
import fear_and_greed

fear_and_greed.get()
```

Returns a three-element namedtuple with (a) the current value of the Fear & Greed Index, (b) a description of the category into which the index value falls (from "Extreme Fear" to "Extreme Greed") and (c) the timestamp at which the index value was last updated on CNN's website. Example:

```python
FearGreedIndex(
    value=31.4266,
    description='fear',
    last_update=datetime.datetime(2022, 4, 25, 16, 51, 9, 254000, tzinfo=datetime.timezone.utc),
 )
```

## Fetch Historical Fear & Greed Data

```python
historical_data = fear_and_greed.historical()
```
The historical function provides a list of historical Fear & Greed Index values, each with its corresponding description and timestamp.

```python
[
    FearGreedIndex(
        value=80.0,
        description='extreme greed',
        last_update=datetime.datetime(2022, 4, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ),
    FearGreedIndex(
        value=60.5,
        description='greed',
        last_update=datetime.datetime(2022, 4, 21, 0, 0, 0, tzinfo=datetime.timezone.utc)
    )
]
...
```

## Features
* Fetch the current Fear & Greed Index value along with its description and timestamp.
* Retrieve historical Fear & Greed Index data to analyze trends.

## Testing
The package includes both unit tests and integration tests:

### Unit Tests
Unit tests use mocked data to verify the library's functionality without making actual API requests:

```bash
python -m unittest tests/test_cnn.py
```

### Integration Tests
Integration tests verify that the live CNN Fear & Greed Index API is working as expected. By default, these tests are skipped. To run them:

```bash
RUN_INTEGRATION_TESTS=1 python -m unittest tests/test_endpoints.py
```

The integration tests are also run daily via GitHub Actions to ensure the API remains compatible with this library.

[![Test workflow](https://github.com/vterron/fear-and-greed/actions/workflows/test.yml/badge.svg)](https://github.com/vterron/fear-and-greed/actions/workflows/test.yml)
[![PyPI badge](https://img.shields.io/pypi/v/fear-and-greed?color=blue)](https://pypi.org/project/fear-and-greed/)
[![Black badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
