import pytest
from cryptoadvance.specter.managers.ticker_manager import TickerManager
from cryptoadvance.specter.managers.config_manager import ConfigManager

pytest.mark.skip(reasonn="")


def test_TickerManager(empty_data_folder):
    cm = ConfigManager(data_folder=empty_data_folder)
    tm = TickerManager(cm)

    assert len(tm.get_potential_classes()) == 2

    # assert float(tm.get_price_at("eur"))
