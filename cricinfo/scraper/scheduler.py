import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraper.match_scraper import MatchScraper
from scraper.data_store import DataStore
from scraper.types import Match, MatchStatus

logger = logging.getLogger(__name__)

class MatchScheduler:
    """Scheduler for cricket match scraping"""
    
    def __init__(self, data_store: DataStore):
        """Initialize the match scheduler"""
        self.data_store = data_store
        self.driver = None
        self.match_list = []
        self.active_scrapers = {}  # Dictionary of active scrapers
        self.is_running = False
    
    def initialize(self):
        """Initialize the scheduler"""
        try:
            logger.info("Initializing scheduler")
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set user agent
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            self.is_running = True
            logger.info("Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}", exc_info=True)
            raise
    
    def update_match_list(self):
        """Update the list of upcoming matches"""
        if not self.driver or not self.is_running:
            return
        
        try:
            logger.info("Updating match list")
            
            # Navigate to the match list page
            self.driver.get("https://crex.live/fixtures/match-list")
            
            # Wait for the page to load
            time.sleep(5)
            
            # Extract match data using JavaScript
            matches = self.driver.execute_script("""
                const matchElements = document.querySelectorAll(".match-card");
                return Array.from(matchElements).map(element => {
                    const id = element.getAttribute("data-match-id") || "";
                    const teams = element.querySelector(".teams")?.textContent?.trim() || "";
                    const format = element.querySelector(".format")?.textContent?.trim() || "";
                    const dateTimeStr = element.querySelector(".date-time")?.textContent?.trim() || "";
                    const url = element.querySelector("a")?.getAttribute("href") || "";
                    
                    return {
                        id,
                        teams,
                        format,
                        dateTime: dateTimeStr,
                        url,
                        status: "UPCOMING"
                    };
                });
            """)
            
            # Process match data
            processed_matches = []
            for match in matches:
                try:
                    # Parse date and time
                    match_datetime = datetime.strptime(match['dateTime'], "%d %b %Y, %H:%M %Z")
                    match['dateTime'] = match_datetime.isoformat()
                    processed_matches.append(match)
                except Exception as e:
                    logger.warning(f"Failed to process match: {str(e)}")
            
            # Update match list
            self.match_list = processed_matches
            
            # Store match list in data store
            self.data_store.store_match_list(processed_matches)
            
            logger.info(f"Updated match list with {len(processed_matches)} matches")
            
        except Exception as e:
            logger.error(f"Failed to update match list: {str(e)}", exc_info=True)
    
    def check_match_status(self):
        """Check status of matches and start/stop scrapers as needed"""
        if not self.is_running:
            return
        
        try:
            now = datetime.now()
            
            # Check each match
            for match in self.match_list:
                match_id = match['id']
                match_time = datetime.fromisoformat(match['dateTime'])
                
                # If match is about to start (within 5 minutes) and no scraper is running
                if (match_time - now <= timedelta(minutes=5) and 
                    match_time > now and 
                    match_id not in self.active_scrapers):
                    
                    logger.info(f"Match {match_id} is about to start, preparing scraper")
                    
                    # Create and initialize match scraper
                    scraper = MatchScraper(match_id, match['url'], self.data_store)
                    scraper.initialize()
                    
                    # Add to active scrapers
                    self.active_scrapers[match_id] = scraper
                    
                    # Update match status
                    match['status'] = MatchStatus.UPCOMING
                    self.data_store.update_match_status(match_id, MatchStatus.UPCOMING)
                
                # If match has started and scraper is not in LIVE mode
                if (match_time <= now and 
                    match_id in self.active_scrapers and 
                    match['status'] != MatchStatus.LIVE):
                    
                    logger.info(f"Match {match_id} has started, switching to live mode")
                    
                    # Get scraper and switch to live mode
                    scraper = self.active_scrapers[match_id]
                    scraper.start_live_tracking()
                    
                    # Update match status
                    match['status'] = MatchStatus.LIVE
                    self.data_store.update_match_status(match_id, MatchStatus.LIVE)
                
                # Check if any live match has ended
                if match['status'] == MatchStatus.LIVE and match_id in self.active_scrapers:
                    scraper = self.active_scrapers[match_id]
                    is_match_ended = scraper.check_if_match_ended()
                    
                    if is_match_ended:
                        logger.info(f"Match {match_id} has ended, stopping scraper")
                        
                        # Stop the scraper
                        scraper.stop()
                        del self.active_scrapers[match_id]
                        
                        # Update match status
                        match['status'] = MatchStatus.COMPLETED
                        self.data_store.update_match_status(match_id, MatchStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"Error checking match status: {str(e)}", exc_info=True)
    
    def stop(self):
        """Stop the scheduler and all active scrapers"""
        logger.info("Stopping scheduler")
        self.is_running = False
        
        # Stop all active scrapers
        for match_id, scraper in list(self.active_scrapers.items()):
            logger.info(f"Stopping scraper for match {match_id}")
            scraper.stop()
            del self.active_scrapers[match_id]
        
        # Close browser
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        logger.info("Scheduler stopped")
    
    def get_status(self):
        """Get status information about the scheduler"""
        upcoming_matches = sum(1 for m in self.match_list if m['status'] == MatchStatus.UPCOMING)
        live_matches = sum(1 for m in self.match_list if m['status'] == MatchStatus.LIVE)
        completed_matches = sum(1 for m in self.match_list if m['status'] == MatchStatus.COMPLETED)
        
        return {
            "is_running": self.is_running,
            "match_count": len(self.match_list),
            "active_scrapers": list(self.active_scrapers.keys()),
            "upcoming_matches": upcoming_matches,
            "live_matches": live_matches,
            "completed_matches": completed_matches
        }