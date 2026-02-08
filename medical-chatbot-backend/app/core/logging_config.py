import logging
import sys
import os
from pathlib import Path

def setup_logging():
    """Configure logging for the application to file and console"""
    # Create logs directory in the project root (up 2 levels from app/core)
    # medical-chatbot-backend/logs
    base_dir = Path(os.getcwd())
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Log file path
    log_file = log_dir / "medical_chatbot.log"
    
    # Format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Root Logger Configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Specific loggers
    logging.getLogger("uvicorn.access").propagate = True
    
    logging.info(f"Logging configured. Logs writing to: {log_file}")
    
    return log_file
