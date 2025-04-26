import os
import logging
from datetime import datetime

class Logger:
    """Custom logger for the cricket scraper"""
    
    def __init__(self, name="cricket_scraper"):
        """Initialize the logger"""
        self.name = name
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create file handler
        log_file = os.path.join(self.logs_dir, f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=True):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

# Create default logger instance
cricket_logger = Logger()