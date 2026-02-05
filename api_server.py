"""
API Server Entry Point

Run with:
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

Or with the run script:
    python api_server.py
"""

import uvicorn
from src.api.routes import app
from src.utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_file_logging=True)
logger = get_logger('api_server')


def main():
    """Run the API server."""
    logger.info("Starting Oncology irAE Detection API server...")
    
    uvicorn.run(
        "src.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
