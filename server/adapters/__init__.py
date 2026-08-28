"""Adapters package for Aviator bot."""

from .base_adapter import BaseAdapter, AdapterMode
from .onexbet_adapter import OnexbetAdapter

__all__ = ["BaseAdapter", "AdapterMode", "OnexbetAdapter"]
