from datetime import datetime
from unittest.mock import MagicMock
from urllib.error import HTTPError
import pytest

import requests
from cryptoadvance.specter.specter_error import SpecterError
from cryptoadvance.specter.ticker.ticker_provider import (
    BitstampTickerProvider,
    CoindeskTickerProvider,
)
from cryptoadvance.specter.util.price_providers import currency_mapping
from json.decoder import JSONDecodeError
from requests import session


@pytest.mark.skip()
def test_BitstampTickerProvider():
    assert BitstampTickerProvider.provider_id() == "bitstamp"

    assert "bitstamp" in currency_mapping["eur"]["support"]
    assert BitstampTickerProvider.supports_currency("eur")
    b = BitstampTickerProvider(False)

    # happy path
    price, symbol = b.get_price_at(requests.session(), "eur", timestamp="now")
    assert float(price)
    assert symbol == "€"

    # 404
    with pytest.raises(SpecterError):
        price, symbol = b.get_price_at(mock_session_404(), timestamp="now")


@pytest.mark.skip()
def test_CoindeskTickerProvider():
    assert CoindeskTickerProvider.provider_id() == "coindesk"

    assert "coindesk" in currency_mapping["eur"]["support"]
    assert CoindeskTickerProvider.supports_currency("eur")
    b = CoindeskTickerProvider(False)

    # happy path
    price, symbol = b.get_price_at(requests.session(), timestamp="now")
    assert float(price)
    assert symbol == "€"

    # 404
    with pytest.raises(SpecterError):
        price, symbol = b.get_price_at(mock_session_404(), timestamp="now")


def mock_session_404():
    # 404
    mock_session = MagicMock()
    response_mock = MagicMock()
    response_mock.json.side_effect = JSONDecodeError("fake error", "meh", 5)
    response_mock.status_code = 404
    response_mock.raise_for_status.side_effect = HTTPError(
        "Fake Error", "meh", "moh", "mah", "mih"
    )
    response_mock.raise_for_status.side_effect.response = response_mock
    mock_session.get.return_value = response_mock
    return mock_session
