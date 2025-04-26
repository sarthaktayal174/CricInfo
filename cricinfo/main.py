import os
import time
import json
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scheduler import MatchScheduler
from scraper.data_store import DataStore

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, f"cricket_scraper_{datetime.now().strftime('%Y-%m-%d')}.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CricketScraperApp:
    """Main application class for the Cricket Scraper"""
    
    def __init__(self, data_dir="./data"):
        """Initialize the Cricket Scraper application"""
        logger.info("Initializing Cricket Scraper Application")
        
        # Create necessary directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize components
        self.data_store = DataStore(data_dir)
        self.scheduler = MatchScheduler(self.data_store)
        self.background_scheduler = BackgroundScheduler()
        
    def start(self):
        """Start the Cricket Scraper application"""
        try:
            logger.info("Starting Cricket Scraper Application")
            
            # Initialize the scheduler
            self.scheduler.initialize()
            
            # Schedule jobs
            self.background_scheduler.add_job(
                self.scheduler.update_match_list, 
                'interval', 
                minutes=15,
                id='update_match_list'
            )
            
            self.background_scheduler.add_job(
                self.scheduler.check_match_status, 
                'interval', 
                minutes=1,
                id='check_match_status'
            )
            
            # Start the scheduler
            self.background_scheduler.start()
            
            # Initial update of match list
            self.scheduler.update_match_list()
            
            logger.info("Cricket Scraper Application started successfully")
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to start Cricket Scraper Application: {str(e)}", exc_info=True)
            self.stop()
    
    def stop(self):
        """Stop the Cricket Scraper application"""
        logger.info("Stopping Cricket Scraper Application")
        
        # Stop the scheduler
        self.scheduler.stop()
        
        # Shutdown the background scheduler
        if self.background_scheduler.running:
            self.background_scheduler.shutdown()
            
        logger.info("Cricket Scraper Application stopped")
    
    def get_status(self):
        """Get the current status of the application"""
        return {
            "scheduler": self.scheduler.get_status(),
            "data_store": self.data_store.get_storage_stats(),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    app = CricketScraperApp()
    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()