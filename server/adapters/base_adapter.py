"""Base adapter interface for Aviator bot."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class AdapterMode(Enum):
    """Adapter operation mode."""
    SIMULATE = "simulate"
    LIVE = "live"


class BaseAdapter(ABC):
    """Abstract base class for betting adapters."""
    
    def __init__(self, mode: AdapterMode = AdapterMode.SIMULATE, dry_run: bool = True):
        """
        Initialize the adapter.
        
        Args:
            mode: Operation mode (simulate or live)
            dry_run: If True, don't place real bets even in live mode
        """
        self.mode = mode
        self.dry_run = dry_run
        self.is_connected = False
    
    @abstractmethod
    async def connect(self, url: str, username: str, password: str) -> bool:
        """Connect to the betting platform."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the betting platform."""
        pass
    
    @abstractmethod
    async def place_bet(self, amount: float, multiplier: float) -> Dict[str, Any]:
        """Place a bet on Aviator game."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> float:
        """Get current account balance."""
        pass
    
    @abstractmethod
    async def cash_out(self, bet_id: str) -> bool:
        """Cash out an active bet."""
        pass
    
    def should_execute(self) -> bool:
        """Determine if action should be executed based on mode and dry_run."""
        if self.mode == AdapterMode.SIMULATE:
            return False
        return not self.dry_run
