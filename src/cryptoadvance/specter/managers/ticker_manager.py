from requests import Session
from cryptoadvance.specter.ticker.ticker_provider import TickerProvider
from cryptoadvance.specter.util.reflection import (
    get_classlist_of_type_clazz_from_modulelist,
)


class TickerManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.provider_cache = {}

    def get_price_at(self, currency, timestamp="now"):

        # provider: TickerProvider = self.get_provider(self.config_manager.price_provider)

        # if self.config_manager.only_tor or provider.only_tor:
        #    requests_session = create_tor_enabled_requests_session(self.config_manager)
        # else:
        #    requests_session: Session = requests_session
        # return provider.get_price_at(requests_session, currency, timestamp)
        pass

    def get_provider(self, exchange: str, currency: str, tor: bool):
        """searches for a provider and returns one out of the cache if existing (or creates it)"""
        exchange: TickerProvider = self.provider_cache.get(exchange)
        if exchange and exchange.supports_currency(currency):
            return exchange
        self.provider_cache[exchange] = self.get_ticket_provider_for_id(exchange)
        return self.provider_cache.get(exchange)

    @classmethod
    def get_ticket_provider_for_id(claz, id):
        for tp in claz.get_potential_classes():
            if claz.provider_id == id:
                return claz(False)
        return None

    @classmethod
    def get_potential_classes(claz) -> list:
        return get_classlist_of_type_clazz_from_modulelist(
            TickerProvider, ["cryptoadvance.specter.ticker.ticker_provider"]
        )
