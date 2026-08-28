"""Configuration management for the Aviator bot server."""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Server configuration settings."""
    
    # Server mode
    START_MODE: str = os.getenv("START_MODE", "simulate")
    
    # Adapter settings
    LIVE: bool = os.getenv("LIVE", "false").lower() == "true"
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    
    # Browser settings
    HEADFUL: bool = os.getenv("HEADFUL", "false").lower() == "true"
    
    # 1xBet credentials
    ONE_XBET_URL: str = os.getenv("ONE_XBET_URL", "https://1xbet.com/aviator")
    LOGIN_USERNAME: Optional[str] = os.getenv("LOGIN_USERNAME")
    LOGIN_PASSWORD: Optional[str] = os.getenv("LOGIN_PASSWORD")
    
    @property
    def is_simulate_mode(self) -> bool:
        """Check if server is in simulate mode."""
        return self.START_MODE.lower() == "simulate"
    
    @property
    def is_live_mode(self) -> bool:
        """Check if live mode is enabled."""
        return self.LIVE and not self.is_simulate_mode
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "START_MODE": self.START_MODE,
            "LIVE": self.LIVE,
            "DRY_RUN": self.DRY_RUN,
            "HEADFUL": self.HEADFUL,
            "ONE_XBET_URL": self.ONE_XBET_URL,
            "LOGIN_USERNAME": self.LOGIN_USERNAME,
        }


# Global config instance
config = Config()
