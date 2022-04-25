import logging
from urllib.error import HTTPError

import requests
from cryptoadvance.specter.specter_error import SpecterError, handle_exception

from ..util.common import camelcase2snake_case, snake_case2camelcase
from ..util.price_providers import currency_mapping
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)


class TickerProvider:
    def __init__(self, tor):
        self.tor = tor

    @classmethod
    def provider_id(claz):
        """A Provider Called SpotbitBitstampTickerProvider gets an ID of spotbit_bitstamp"""
        return camelcase2snake_case(claz.__name__.replace("TickerProvider", ""))

    @classmethod
    def supports_currency(claz, currency):
        logger.debug("provider_id = ")
        if claz.provider_id() in currency_mapping[currency].get("support"):
            return True
        return False

    def get_price_at(claz, specter, currency, timestamp="now"):
        if not claz.supports_currency(currency):
            raise SpecterError(
                f"Currency {currency} not supported by {self.__class__.__name__}"
            )
        pass

    @classmethod
    def failsafe_request_get(claz, requests_session, url):
        """wrapping requests which is only emitting reasonable SpecterErrors and HttpErrors which are hopefully meaningful to the user"""
        try:
            response: requests.Response = requests_session.get(url)
            if response.status_code != 200:
                response.raise_for_status()
            json_response = response.json()
            if json_response.get("errors"):
                raise SpecterError(f"JSON error: {json_response}")
            return response.json()
        except HTTPError as httpe:
            try:
                json_response = response.json()
            except JSONDecodeError:
                raise SpecterError(f"HttpError {httpe.response.status_code} for {url}")
            logger.debug(f"json-response: {json_response}")
            if json_response.get("errors"):
                raise SpecterError(f"JSON error: {json_response}")
            raise SpecterError(f"HttpError {httpe.response.status_code} for {url}")
        except JSONDecodeError as jde:
            logger.error(f"JSONDecodeError while trying to parse: {response.text}")
            raise SpecterError(f"The service returned {response.text}")


class BitstampTickerProvider(TickerProvider):
    def get_price_at(self, session, currency, timestamp="now"):
        if timestamp == "now":
            price = self.failsafe_request_get(
                session,
                "https://www.bitstamp.net/api/v2/ticker/btc{}".format(currency),
            )["last"]
        else:
            price = self.failsafe_request_get(
                session,
                "https://www.bitstamp.net/api/v2/ohlc/btc{}/?limit=1&step=86400&start={}".format(
                    currency, timestamp
                ),
            )["data"]["ohlc"][0]["close"]
        return (price, currency_mapping[currency]["symbol"])


class CoindeskTickerProvider(TickerProvider):
    def get_price_at(self, session, currency, timestamp="now"):
        if timestamp == "now":
            price = self.failsafe_request_get(
                session,
                f"https://api.coindesk.com/v1/bpi/currentprice/{self.currency.upper()}.json",
            )["bpi"][self.currency.upper()]["rate_float"]
        else:
            raise SpecterError("coindesk does not support historic prices")
        return (price, currency_mapping[currency]["symbol"])
