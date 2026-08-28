"""Main FastAPI application for Aviator bot server."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from adapters import OnexbetAdapter, AdapterMode


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Aviator Bot Server",
    description="Server for Aviator betting bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global adapter instance
adapter: OnexbetAdapter = None


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    global adapter
    
    logger.info(f"Starting server in {config.START_MODE} mode")
    logger.info(f"Configuration: {config.to_dict()}")
    
    # Initialize adapter
    mode = AdapterMode.SIMULATE if config.is_simulate_mode else AdapterMode.LIVE
    adapter = OnexbetAdapter(
        mode=mode,
        dry_run=config.DRY_RUN,
        headful=config.HEADFUL
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    if adapter and adapter.is_connected:
        await adapter.disconnect()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Aviator Bot Server",
        "mode": config.START_MODE,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "adapter_connected": adapter.is_connected if adapter else False,
        "mode": config.START_MODE
    }


@app.get("/config")
async def get_config():
    """Get current configuration."""
    return config.to_dict()


@app.post("/api/adapter/1xbet/connect")
async def connect_1xbet(live: bool = False):
    """
    Connect to 1xBet adapter.
    
    Args:
        live: Whether to enable live mode
    """
    try:
        if not config.LOGIN_USERNAME or not config.LOGIN_PASSWORD:
            raise HTTPException(status_code=400, detail="Missing login credentials in .env")
        
        # Determine mode based on parameter and config
        if live and config.LIVE:
            mode = AdapterMode.LIVE
        else:
            mode = AdapterMode.SIMULATE
        
        # Recreate adapter with new mode
        global adapter
        adapter = OnexbetAdapter(
            mode=mode,
            dry_run=config.DRY_RUN,
            headful=config.HEADFUL
        )
        
        success = await adapter.connect(
            url=config.ONE_XBET_URL,
            username=config.LOGIN_USERNAME,
            password=config.LOGIN_PASSWORD
        )
        
        if success:
            return {
                "success": True,
                "message": "Connected to 1xBet",
                "mode": mode.value
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to connect")
            
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adapter/1xbet/disconnect")
async def disconnect_1xbet():
    """Disconnect from 1xBet adapter."""
    try:
        if adapter:
            await adapter.disconnect()
        return {"success": True, "message": "Disconnected from 1xBet"}
    except Exception as e:
        logger.error(f"Disconnection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adapter/1xbet/place-bet")
async def place_bet(amount: float, multiplier: float):
    """Place a bet on Aviator."""
    try:
        if not adapter:
            raise HTTPException(status_code=503, detail="Adapter not initialized")
        
        if not adapter.is_connected:
            raise HTTPException(status_code=503, detail="Adapter not connected")
        
        result = await adapter.place_bet(amount, multiplier)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Bet placement failed"))
            
    except Exception as e:
        logger.error(f"Bet placement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adapter/1xbet/cashout")
async def cashout_bet(bet_id: str):
    """Cash out an active bet."""
    try:
        if not adapter:
            raise HTTPException(status_code=503, detail="Adapter not initialized")
        
        success = await adapter.cash_out(bet_id)
        
        if success:
            return {"success": True, "message": f"Bet {bet_id} cashed out"}
        else:
            raise HTTPException(status_code=400, detail="Cashout failed")
            
    except Exception as e:
        logger.error(f"Cashout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adapter/1xbet/balance")
async def get_balance():
    """Get current balance."""
    try:
        if not adapter:
            raise HTTPException(status_code=503, detail="Adapter not initialized")
        
        balance = await adapter.get_balance()
        return {"balance": balance}
        
    except Exception as e:
        logger.error(f"Balance retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adapter/1xbet/bets")
async def get_active_bets():
    """Get all active bets."""
    try:
        if not adapter:
            raise HTTPException(status_code=503, detail="Adapter not initialized")
        
        bets = adapter.get_active_bets()
        return {
            "bets": [
                {
                    "bet_id": bet.bet_id,
                    "amount": bet.amount,
                    "multiplier": bet.multiplier,
                    "status": bet.status,
                    "timestamp": bet.timestamp.isoformat()
                }
                for bet in bets.values()
            ]
        }
        
    except Exception as e:
        logger.error(f"Bets retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=config.START_MODE == "simulate"
    )
