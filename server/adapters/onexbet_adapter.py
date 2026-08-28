"""1xBet adapter for Aviator bot - Full Live Implementation."""

import asyncio
import logging
import random
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .base_adapter import BaseAdapter, AdapterMode


logger = logging.getLogger(__name__)


class BetStatus(Enum):
    """Bet status enumeration."""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    CASHED_OUT = "cashed_out"


@dataclass
class BetResult:
    """Result of a bet placement."""
    bet_id: str
    amount: float
    multiplier: float
    status: str  # "pending", "won", "lost", "cashed_out"
    timestamp: datetime
    crash_point: Optional[float] = None
    payout: Optional[float] = None


class OnexbetAdapter(BaseAdapter):
    """1xBet adapter for placing bets on Aviator game."""
    
    def __init__(self, mode: AdapterMode = AdapterMode.SIMULATE, dry_run: bool = True, headful: bool = False):
        """
        Initialize 1xBet adapter.
        
        Args:
            mode: Operation mode (simulate or live)
            dry_run: If True, don't place real bets even in live mode
            headful: If True, run browser with UI visible
        """
        super().__init__(mode, dry_run)
        self.headful = headful
        self.url: Optional[str] = None
        self.username: Optional[str] = None
        self.balance: float = 1000.0  # Initial balance
        self.active_bets: Dict[str, BetResult] = {}
        self.bet_counter: int = 0
        self.browser = None
        self.page = None
        self.game_session = None
        
        # Live mode imports
        try:
            from playwright.async_api import async_playwright, Browser, Page
            self.playwright = async_playwright
            self.Browser = Browser
            self.Page = Page
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False
            logger.warning("Playwright not installed. Install with: pip install playwright")
    
    async def connect(self, url: str, username: str, password: str) -> bool:
        """
        Connect to 1xBet and login.
        
        Args:
            url: 1xBet URL
            username: Login username
            password: Login password
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.url = url
            self.username = username
            
            if self.mode == AdapterMode.SIMULATE:
                logger.info(f"[SIMULATE] Connecting to {url} with user {username}")
                self.is_connected = True
                return True
            
            # Live mode - Initialize browser with Playwright
            if not self.playwright_available:
                logger.error("Playwright not available. Install with: pip install playwright")
                return False
            
            logger.info(f"[LIVE] Connecting to {url} with user {username}")
            
            # Launch browser
            p = await self.playwright().start()
            self.browser = await p.chromium.launch(headless=not self.headful)
            self.page = await self.browser.new_page()
            
            # Set user agent to mimic real browser
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Navigate to 1xBet
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until='networkidle')
            
            # Login
            await self._login_live(username, password)
            
            self.is_connected = True
            logger.info("Successfully connected to 1xBet")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            if self.browser:
                await self.browser.close()
            return False
    
    async def _login_live(self, username: str, password: str) -> None:
        """Perform login on 1xBet website."""
        try:
            # Wait for login form elements
            # These selectors may need adjustment based on current 1xBet UI
            logger.info("Logging in...")
            
            # Click login button if needed
            try:
                await self.page.click('[data-test-id="login-button"]', timeout=5000)
            except:
                pass
            
            # Fill username
            username_input = await self.page.query_selector('[name="login"]')
            if username_input:
                await username_input.fill(username)
            else:
                await self.page.fill('input[type="text"]', username)
            
            # Fill password
            password_input = await self.page.query_selector('[name="password"]')
            if password_input:
                await password_input.fill(password)
            else:
                await self.page.fill('input[type="password"]', password)
            
            # Submit login
            await self.page.click('button:has-text("Sign in")', timeout=10000)
            
            # Wait for dashboard/game to load
            await self.page.wait_for_url("**/aviator**", timeout=15000)
            
            logger.info("Login successful")
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect and cleanup."""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
            self.is_connected = False
            logger.info("Disconnected from 1xBet")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def place_bet(self, amount: float, multiplier: float) -> Dict[str, Any]:
        """
        Place a bet on Aviator game.
        
        Args:
            amount: Bet amount
            multiplier: Target cashout multiplier
            
        Returns:
            Bet placement result
        """
        if not self.is_connected:
            return {"success": False, "error": "Not connected"}
        
        if amount <= 0:
            return {"success": False, "error": "Invalid amount"}
        
        if self.mode == AdapterMode.SIMULATE:
            return self._simulate_bet(amount, multiplier)
        
        if self.should_execute():
            return await self._place_live_bet(amount, multiplier)
        else:
            return self._simulate_bet(amount, multiplier)
    
    def _simulate_bet(self, amount: float, multiplier: float) -> Dict[str, Any]:
        """Simulate a bet placement."""
        self.bet_counter += 1
        bet_id = f"SIM-{self.bet_counter}"
        
        if amount > self.balance:
            return {"success": False, "error": "Insufficient balance"}
        
        # Deduct bet amount
        self.balance -= amount
        
        # Simulate crash point and outcome
        crash_point = round(random.uniform(1.0, 5.0), 2)
        won = crash_point >= multiplier
        payout = amount * multiplier if won else 0
        
        if won:
            self.balance += payout
        
        # Create simulated bet
        bet = BetResult(
            bet_id=bet_id,
            amount=amount,
            multiplier=multiplier,
            status=BetStatus.WON.value if won else BetStatus.LOST.value,
            timestamp=datetime.now(),
            crash_point=crash_point,
            payout=payout
        )
        self.active_bets[bet_id] = bet
        
        logger.info(f"[SIMULATE] Bet {bet_id}: Amount={amount}, Target={multiplier}x, "
                   f"Crash={crash_point}x, Result={'WON' if won else 'LOST'}, Payout={payout}")
        
        return {
            "success": True,
            "bet_id": bet_id,
            "amount": amount,
            "multiplier": multiplier,
            "crash_point": crash_point,
            "payout": payout,
            "mode": "simulate"
        }
    
    async def _place_live_bet(self, amount: float, multiplier: float) -> Dict[str, Any]:
        """Place a live bet on 1xBet."""
        try:
            self.bet_counter += 1
            bet_id = f"LIVE-{self.bet_counter}"
            
            logger.info(f"[LIVE] Placing bet - Amount: {amount}, Target: {multiplier}x")
            
            # Find and fill bet amount input
            amount_input = await self.page.query_selector('[data-test-id="bet-amount"]')
            if amount_input:
                await amount_input.fill(str(amount))
            else:
                # Fallback selector
                await self.page.fill('input[placeholder*="Amount"]', str(amount))
            
            # Click place bet button
            await self.page.click('[data-test-id="place-bet"]', timeout=5000)
            
            # Wait for bet confirmation
            await self.page.wait_for_selector('[data-test-id="bet-placed"]', timeout=10000)
            
            # Store bet info
            bet = BetResult(
                bet_id=bet_id,
                amount=amount,
                multiplier=multiplier,
                status=BetStatus.PENDING.value,
                timestamp=datetime.now()
            )
            self.active_bets[bet_id] = bet
            
            logger.info(f"[LIVE] Bet placed successfully: {bet_id}")
            
            return {
                "success": True,
                "bet_id": bet_id,
                "amount": amount,
                "multiplier": multiplier,
                "mode": "live"
            }
            
        except Exception as e:
            logger.error(f"[LIVE] Bet placement failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_balance(self) -> float:
        """Get current account balance."""
        try:
            if self.mode == AdapterMode.SIMULATE:
                logger.info(f"[SIMULATE] Balance: ${self.balance}")
                return self.balance
            
            # Live mode - fetch from page
            balance_element = await self.page.query_selector('[data-test-id="balance"]')
            if balance_element:
                balance_text = await balance_element.text_content()
                # Parse balance from text (e.g., "$1000.00")
                balance_value = float(''.join(c for c in balance_text if c.isdigit() or c == '.'))
                self.balance = balance_value
                logger.info(f"[LIVE] Balance: ${self.balance}")
                return self.balance
            
            return self.balance
            
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return self.balance
    
    async def cash_out(self, bet_id: str) -> bool:
        """Cash out an active bet."""
        try:
            if bet_id not in self.active_bets:
                logger.warning(f"Bet not found: {bet_id}")
                return False
            
            bet = self.active_bets[bet_id]
            
            if self.mode == AdapterMode.SIMULATE:
                logger.info(f"[SIMULATE] Cashing out bet {bet_id}")
                # Simulate win at 2x multiplier
                current_multiplier = 2.0
                if current_multiplier >= bet.multiplier:
                    payout = bet.amount * bet.multiplier
                    self.balance += payout
                    bet.status = BetStatus.CASHED_OUT.value
                    bet.payout = payout
                    logger.info(f"[SIMULATE] Cashout successful! Payout: ${payout}")
                    return True
                else:
                    logger.info(f"[SIMULATE] Cashout failed - multiplier too low")
                    return False
            
            if self.should_execute():
                logger.info(f"[LIVE] Cashing out bet {bet_id}")
                
                # Click cashout button for specific bet
                cashout_button = await self.page.query_selector(f'[data-bet-id="{bet_id}"] [data-test-id="cashout"]')
                if cashout_button:
                    await cashout_button.click()
                    
                    # Wait for cashout confirmation
                    await self.page.wait_for_selector('[data-test-id="cashout-confirmed"]', timeout=5000)
                    
                    bet.status = BetStatus.CASHED_OUT.value
                    logger.info(f"[LIVE] Cashout successful: {bet_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cashout error: {e}")
            return False
    
    def get_active_bets(self) -> Dict[str, BetResult]:
        """Get all active bets."""
        return self.active_bets.copy()
    
    def clear_bets(self) -> None:
        """Clear all bets (for testing)."""
        self.active_bets.clear()
    
    async def auto_cashout(self, bet_id: str, target_multiplier: float) -> None:
        """
        Monitor a bet and auto cashout at target multiplier.
        
        Args:
            bet_id: ID of bet to monitor
            target_multiplier: Target multiplier for cashout
        """
        try:
            logger.info(f"Monitoring bet {bet_id}, will cashout at {target_multiplier}x")
            
            while bet_id in self.active_bets:
                bet = self.active_bets[bet_id]
                
                # Get current multiplier from page
                multiplier_element = await self.page.query_selector('[data-test-id="current-multiplier"]')
                if multiplier_element:
                    multiplier_text = await multiplier_element.text_content()
                    current_multiplier = float(multiplier_text.replace('x', ''))
                    
                    logger.info(f"Current multiplier: {current_multiplier}x")
                    
                    if current_multiplier >= target_multiplier:
                        success = await self.cash_out(bet_id)
                        if success:
                            logger.info(f"Auto cashout successful at {current_multiplier}x")
                        break
                
                await asyncio.sleep(0.1)  # Poll every 100ms
        
        except Exception as e:
            logger.error(f"Auto cashout error: {e}")
