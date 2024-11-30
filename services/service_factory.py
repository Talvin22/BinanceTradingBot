"""Factory for creating and managing services with shared dependencies"""
from pybit.unified_trading import HTTP
from config import BYBIT_API_KEY, BYBIT_API_SECRET
from .bybit_service import BybitService
from .trading_service import TradingService

class ServiceFactory:
    _instance = None
    _bybit_session = None
    _bybit_service = None
    _trading_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            # Initialize shared Bybit session for testnet
            cls._bybit_session = HTTP(
                api_key=BYBIT_API_KEY,
                api_secret=BYBIT_API_SECRET,
                testnet=True  # Using testnet for all operations
            )
        return cls._instance

    @property
    def bybit_service(self) -> BybitService:
        """Get or create BybitService instance"""
        if self._bybit_service is None:
            self._bybit_service = BybitService(self._bybit_session)
        return self._bybit_service

    @property
    def trading_service(self) -> TradingService:
        """Get or create TradingService instance"""
        if self._trading_service is None:
            self._trading_service = TradingService(self._bybit_session)
        return self._trading_service