import logging
import time
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.data_store import DataStore

logger = logging.getLogger(__name__)

class MatchScraper:
    """Scraper for individual cricket matches"""
    
    def __init__(self, match_id: str, match_url: str, data_store: DataStore):
        """Initialize the match scraper"""
        self.match_id = match_id
        self.match_url = match_url
        self.data_store = data_store
        self.driver = None
        self.is_tracking = False
        self.tracking_thread = None
        self.stop_event = threading.Event()
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def initialize(self):
        """Initialize the match scraper"""
        try:
            logger.info(f"Initializing scraper for match {self.match_id}")
            
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
            
            # Navigate to match page
            self.driver.get(self.match_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Scrape initial match info and squads
            self.scrape_match_info()
            self.scrape_squads()
            
            logger.info(f"Scraper initialized for match {self.match_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize scraper for match {self.match_id}: {str(e)}", exc_info=True)
            
            # Retry initialization if not exceeded max retries
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"Retrying initialization for match {self.match_id} ({self.retry_count}/{self.max_retries})")
                
                # Wait before retrying
                time.sleep(self.retry_delay)
                self.initialize()
            else:
                raise
    
    def scrape_match_info(self):
        """Scrape match information"""
        try:
            logger.info(f"Scraping match info for {self.match_id}")
            
            # Click on the "Match Info" tab if not already active
            match_info_tab = self.driver.find_elements(By.CSS_SELECTOR, ".tab-match-info:not(.active)")
            if match_info_tab:
                match_info_tab[0].click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".match-info-container"))
                )
            
            # Extract match information using JavaScript
            match_info = self.driver.execute_script("""
                const infoContainer = document.querySelector(".match-info-container");
                if (!infoContainer) return null;
                
                return {
                    teams: {
                        home: {
                            name: document.querySelector(".team-home .team-name")?.textContent?.trim() || "",
                            shortName: document.querySelector(".team-home .team-short-name")?.textContent?.trim() || ""
                        },
                        away: {
                            name: document.querySelector(".team-away .team-name")?.textContent?.trim() || "",
                            shortName: document.querySelector(".team-away .team-short-name")?.textContent?.trim() || ""
                        }
                    },
                    matchDetails: {
                        series: document.querySelector(".series-name")?.textContent?.trim() || "",
                        format: document.querySelector(".match-format")?.textContent?.trim() || "",
                        venue: document.querySelector(".venue-name")?.textContent?.trim() || "",
                        date: document.querySelector(".match-date")?.textContent?.trim() || "",
                        time: document.querySelector(".match-time")?.textContent?.trim() || "",
                        toss: document.querySelector(".toss-result")?.textContent?.trim() || "",
                        umpires: Array.from(document.querySelectorAll(".umpire")).map(el => el.textContent?.trim() || "")
                    }
                };
            """)
            
            if not match_info:
                raise Exception("Failed to extract match information")
            
            # Store match info in data store
            self.data_store.store_match_info(self.match_id, match_info)
            
            logger.info(f"Successfully scraped match info for {self.match_id}")
            
        except Exception as e:
            logger.error(f"Error scraping match info for {self.match_id}: {str(e)}", exc_info=True)
            raise
    
    def scrape_squads(self):
        """Scrape team squads"""
        try:
            logger.info(f"Scraping squads for {self.match_id}")
            
            # Click on the "Squads" tab
            squads_tab = self.driver.find_elements(By.CSS_SELECTOR, ".tab-squads:not(.active)")
            if squads_tab:
                squads_tab[0].click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".squads-container"))
                )
            
            # Extract squads information using JavaScript
            squads = self.driver.execute_script("""
                const squadsContainer = document.querySelector(".squads-container");
                if (!squadsContainer) return null;
                
                // Function to extract players from a team container
                const extractPlayers = (teamSelector) => {
                    const players = document.querySelectorAll(`${teamSelector} .player`);
                    return Array.from(players).map(player => {
                        return {
                            name: player.querySelector(".player-name")?.textContent?.trim() || "",
                            role: player.querySelector(".player-role")?.textContent?.trim() || "",
                            isCaptain: !!player.querySelector(".captain-indicator"),
                            isWicketkeeper: !!player.querySelector(".wicketkeeper-indicator")
                        };
                    });
                };
                
                return {
                    homeTeam: {
                        name: document.querySelector(".home-team-name")?.textContent?.trim() || "",
                        players: extractPlayers(".home-team-squad")
                    },
                    awayTeam: {
                        name: document.querySelector(".away-team-name")?.textContent?.trim() || "",
                        players: extractPlayers(".away-team-squad")
                    }
                };
            """)
            
            if not squads:
                raise Exception("Failed to extract squads information")
            
            # Store squads in data store
            self.data_store.store_squads(self.match_id, squads)
            
            logger.info(f"Successfully scraped squads for {self.match_id}")
            
        except Exception as e:
            logger.error(f"Error scraping squads for {self.match_id}: {str(e)}", exc_info=True)
            raise
    
    def start_live_tracking(self):
        """Start live tracking of the match"""
        if self.is_tracking:
            return
        
        try:
            logger.info(f"Starting live tracking for match {self.match_id}")
            self.is_tracking = True
            self.stop_event.clear()
            
            # Create and start tracking thread
            self.tracking_thread = threading.Thread(target=self._live_tracking_worker)
            self.tracking_thread.daemon = True
            self.tracking_thread.start()
            
            logger.info(f"Live tracking started for match {self.match_id}")
            
        except Exception as e:
            self.is_tracking = False
            logger.error(f"Failed to start live tracking for match {self.match_id}: {str(e)}", exc_info=True)
            raise
    
    def _live_tracking_worker(self):
        """Worker function for live tracking thread"""
        try:
            # Initial scrape of live data and scorecard
            self.scrape_live_data()
            self.scrape_scorecard()
            
            # Continue scraping until stopped
            while not self.stop_event.is_set():
                try:
                    self.scrape_live_data()
                    self.scrape_scorecard()
                except Exception as e:
                    logger.error(f"Error during live tracking for match {self.match_id}: {str(e)}", exc_info=True)
                
                # Wait for 30 seconds before next scrape
                self.stop_event.wait(30)
                
        except Exception as e:
            logger.error(f"Live tracking worker failed for match {self.match_id}: {str(e)}", exc_info=True)
    
    def scrape_live_data(self):
        """Scrape live match data"""
        if not self.driver:
            return
        
        try:
            logger.info(f"Scraping live data for {self.match_id}")
            
            # Click on the "Live" tab
            live_tab = self.driver.find_elements(By.CSS_SELECTOR, ".tab-live:not(.active)")
            if live_tab:
                live_tab[0].click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".live-container"))
                )
            
            # Extract live data using JavaScript
            live_data = self.driver.execute_script("""
                const liveContainer = document.querySelector(".live-container");
                if (!liveContainer) return null;
                
                return {
                    currentInnings: document.querySelector(".current-innings")?.textContent?.trim() || "",
                    score: document.querySelector(".current-score")?.textContent?.trim() || "",
                    runRate: document.querySelector(".run-rate")?.textContent?.trim() || "",
                    requiredRunRate: document.querySelector(".required-run-rate")?.textContent?.trim() || "",
                    lastWicket: document.querySelector(".last-wicket")?.textContent?.trim() || "",
                    recentBalls: Array.from(document.querySelectorAll(".recent-ball")).map(el => el.textContent?.trim() || ""),
                    partnership: document.querySelector(".current-partnership")?.textContent?.trim() || "",
                    batsmen: Array.from(document.querySelectorAll(".batsman")).map(el => ({
                        name: el.querySelector(".batsman-name")?.textContent?.trim() || "",
                        runs: el.querySelector(".batsman-runs")?.textContent?.trim() || "",
                        balls: el.querySelector(".batsman-balls")?.textContent?.trim() || "",
                        fours: el.querySelector(".batsman-fours")?.textContent?.trim() || "",
                        sixes: el.querySelector(".batsman-sixes")?.textContent?.trim() || "",
                        strikeRate: el.querySelector(".batsman-strike-rate")?.textContent?.trim() || ""
                    })),
                    bowlers: Array.from(document.querySelectorAll(".bowler")).map(el => ({
                        name: el.querySelector(".bowler-name")?.textContent?.trim() || "",
                        overs: el.querySelector(".bowler-overs")?.textContent?.trim() || "",
                        maidens: el.querySelector(".bowler-maidens")?.textContent?.trim() || "",
                        runs: el.querySelector(".bowler-runs")?.textContent?.trim() || "",
                        wickets: el.querySelector(".bowler-wickets")?.textContent?.trim() || "",
                        economy: el.querySelector(".bowler-economy")?.textContent?.trim() || ""
                    })),
                    matchStatus: document.querySelector(".match-status")?.textContent?.trim() || "",
                    commentary: Array.from(document.querySelectorAll(".commentary-item"))
                        .map(el => ({
                            text: el.querySelector(".commentary-text")?.textContent?.trim() || "",
                            over: el.querySelector(".commentary-over")?.textContent?.trim() || "",
                            timestamp: el.querySelector(".commentary-timestamp")?.textContent?.trim() || ""
                        }))
                        .slice(0, 10) // Get only the last 10 commentary items
                };
            """)
            
            if not live_data:
                raise Exception("Failed to extract live data")
            
            # Store live data in data store
            self.data_store.store_live_data(self.match_id, live_data)
            
            logger.info(f"Successfully scraped live data for {self.match_id}")
            
        except Exception as e:
            logger.error(f"Error scraping live data for {self.match_id}: {str(e)}", exc_info=True)
            raise
    
    def scrape_scorecard(self):
        """Scrape scorecard data"""
        if not self.driver:
            return
        
        try:
            logger.info(f"Scraping scorecard for {self.match_id}")
            
            # Click on the "Scorecard" tab
            scorecard_tab = self.driver.find_elements(By.CSS_SELECTOR, ".tab-scorecard:not(.active)")
            if scorecard_tab:
                scorecard_tab[0].click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".scorecard-container"))
                )
            
            # Extract scorecard data using JavaScript
            scorecard = self.driver.execute_script("""
                const scorecardContainer = document.querySelector(".scorecard-container");
                if (!scorecardContainer) return null;
                
                // Function to extract innings data
                const extractInnings = (inningsSelector) => {
                    const inningsElement = document.querySelector(inningsSelector);
                    if (!inningsElement) return null;
                    
                    return {
                        team: inningsElement.querySelector(".innings-team")?.textContent?.trim() || "",
                        totalScore: inningsElement.querySelector(".innings-total")?.textContent?.trim() || "",
                        overs: inningsElement.querySelector(".innings-overs")?.textContent?.trim() || "",
                        extras: inningsElement.querySelector(".innings-extras")?.textContent?.trim() || "",
                        batsmen: Array.from(inningsElement.querySelectorAll(".batsman-row")).map(row => ({
                            name: row.querySelector(".batsman-name")?.textContent?.trim() || "",
                            dismissal: row.querySelector(".batsman-dismissal")?.textContent?.trim() || "",
                            runs: row.querySelector(".batsman-runs")?.textContent?.trim() || "",
                            balls: row.querySelector(".batsman-balls")?.textContent?.trim() || "",
                            fours: row.querySelector(".batsman-fours")?.textContent?.trim() || "",
                            sixes: row.querySelector(".batsman-sixes")?.textContent?.trim() || "",
                            strikeRate: row.querySelector(".batsman-strike-rate")?.textContent?.trim() || ""
                        })),
                        bowlers: Array.from(inningsElement.querySelectorAll(".bowler-row")).map(row => ({
                            name: row.querySelector(".bowler-name")?.textContent?.trim() || "",
                            overs: row.querySelector(".bowler-overs")?.textContent?.trim() || "",
                            maidens: row.querySelector(".bowler-maidens")?.textContent?.trim() || "",
                            runs: row.querySelector(".bowler-runs")?.textContent?.trim() || "",
                            wickets: row.querySelector(".bowler-wickets")?.textContent?.trim() || "",
                            economy: row.querySelector(".bowler-economy")?.textContent?.trim() || ""
                        })),
                        fallOfWickets: Array.from(inningsElement.querySelectorAll(".fow-item")).map(
                            item => item.textContent?.trim() || ""
                        )
                    };
                };
                
                // Extract data for all innings (up to 4 for Test matches)
                const innings = [];
                for (let i = 1; i <= 4; i++) {
                    const inningsData = extractInnings(`.innings-${i}`);
                    if (inningsData) {
                        innings.push(inningsData);
                    }
                }
                
                return {
                    innings,
                    matchSummary: document.querySelector(".match-summary")?.textContent?.trim() || "",
                    playerOfTheMatch: document.querySelector(".player-of-match")?.textContent?.trim() || ""
                };
            """)
            
            if not scorecard:
                raise Exception("Failed to extract scorecard data")
            
            # Store scorecard in data store
            self.data_store.store_scorecard(self.match_id, scorecard)
            
            logger.info(f"Successfully scraped scorecard for {self.match_id}")
            
        except Exception as e:
            logger.error(f"Error scraping scorecard for {self.match_id}: {str(e)}", exc_info=True)
            raise
    
    def check_if_match_ended(self):
        """Check if the match has ended"""
        if not self.driver:
            return False
        
        try:
            # Check match status from the page
            is_ended = self.driver.execute_script("""
                const statusElement = document.querySelector(".match-status");
                if (!statusElement) return false;
                
                const status = statusElement.textContent?.trim().toLowerCase() || "";
                return (
                    status.includes("match ended") ||
                    status.includes("completed") ||
                    status.includes("won by") ||
                    status.includes("drawn")
                );
            """)
            
            return is_ended
            
        except Exception as e:
            logger.error(f"Error checking if match {self.match_id} has ended: {str(e)}", exc_info=True)
            return False
    
    def stop(self):
        """Stop the scraper"""
        logger.info(f"Stopping scraper for match {self.match_id}")
        
        # Signal tracking thread to stop
        self.stop_event.set()
        
        # Wait for tracking thread to finish
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=5)
        
        self.is_tracking = False
        
        # Close driver
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        logger.info(f"Scraper stopped for match {self.match_id}")