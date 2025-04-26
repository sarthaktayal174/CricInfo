import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataStore:
    """Data storage for cricket match data"""
    
    def __init__(self, base_dir="./data"):
        """Initialize the data store"""
        self.base_dir = base_dir
        self.match_list_file = os.path.join(self.base_dir, "match-list.json")
        
        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Create matches directory
        os.makedirs(os.path.join(self.base_dir, "matches"), exist_ok=True)
    
    def store_match_list(self, matches: List[Dict[str, Any]]):
        """Store match list"""
        try:
            with open(self.match_list_file, 'w', encoding='utf-8') as f:
                json.dump(matches, f, indent=2)
            
            logger.info(f"Stored {len(matches)} matches in match list")
        except Exception as e:
            logger.error(f"Failed to store match list: {str(e)}", exc_info=True)
            raise
    
    def get_match_list(self) -> List[Dict[str, Any]]:
        """Get match list"""
        try:
            if not os.path.exists(self.match_list_file):
                return []
            
            with open(self.match_list_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to get match list: {str(e)}", exc_info=True)
            return []
    
    def update_match_status(self, match_id: str, status: str):
        """Update match status"""
        try:
            # Get current match list
            matches = self.get_match_list()
            
            # Find and update match status
            for match in matches:
                if match['id'] == match_id:
                    match['status'] = status
                    break
            
            # Store updated match list
            self.store_match_list(matches)
            
            logger.info(f"Updated status of match {match_id} to {status}")
        except Exception as e:
            logger.error(f"Failed to update status of match {match_id}: {str(e)}", exc_info=True)
            raise
    
    def store_match_info(self, match_id: str, match_info: Dict[str, Any]):
        """Store match info"""
        try:
            match_dir = self._get_match_dir(match_id)
            
            # Create match directory if it doesn't exist
            os.makedirs(match_dir, exist_ok=True)
            
            # Write match info to file
            with open(os.path.join(match_dir, "info.json"), 'w', encoding='utf-8') as f:
                json.dump(match_info, f, indent=2)
            
            logger.info(f"Stored info for match {match_id}")
        except Exception as e:
            logger.error(f"Failed to store info for match {match_id}: {str(e)}", exc_info=True)
            raise
    
    def store_squads(self, match_id: str, squads: Dict[str, Any]):
        """Store squads"""
        try:
            match_dir = self._get_match_dir(match_id)
            
            # Create match directory if it doesn't exist
            os.makedirs(match_dir, exist_ok=True)
            
            # Write squads to file
            with open(os.path.join(match_dir, "squads.json"), 'w', encoding='utf-8') as f:
                json.dump(squads, f, indent=2)
            
            logger.info(f"Stored squads for match {match_id}")
        except Exception as e:
            logger.error(f"Failed to store squads for match {match_id}: {str(e)}", exc_info=True)
            raise
    
    def store_live_data(self, match_id: str, live_data: Dict[str, Any]):
        """Store live data"""
        try:
            match_dir = self._get_match_dir(match_id)
            live_dir = os.path.join(match_dir, "live")
            
            # Create live directory if it doesn't exist
            os.makedirs(live_dir, exist_ok=True)
            
            # Generate timestamp for the live data file
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            
            # Write live data to file
            with open(os.path.join(live_dir, f"{timestamp}.json"), 'w', encoding='utf-8') as f:
                json.dump(live_data, f, indent=2)
            
            # Also write to latest.json for easy access
            with open(os.path.join(live_dir, "latest.json"), 'w', encoding='utf-8') as f:
                json.dump(live_data, f, indent=2)
            
            logger.info(f"Stored live data for match {match_id}")
        except Exception as e:
            logger.error(f"Failed to store live data for match {match_id}: {str(e)}", exc_info=True)
            raise
    
    def store_scorecard(self, match_id: str, scorecard: Dict[str, Any]):
        """Store scorecard"""
        try:
            match_dir = self._get_match_dir(match_id)
            scorecard_dir = os.path.join(match_dir, "scorecard")
            
            # Create scorecard directory if it doesn't exist
            os.makedirs(scorecard_dir, exist_ok=True)
            
            # Generate timestamp for the scorecard file
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            
            # Write scorecard to file
            with open(os.path.join(scorecard_dir, f"{timestamp}.json"), 'w', encoding='utf-8') as f:
                json.dump(scorecard, f, indent=2)
            
            # Also write to latest.json for easy access
            with open(os.path.join(scorecard_dir, "latest.json"), 'w', encoding='utf-8') as f:
                json.dump(scorecard, f, indent=2)
            
            logger.info(f"Stored scorecard for match {match_id}")
        except Exception as e:
            logger.error(f"Failed to store scorecard for match {match_id}: {str(e)}", exc_info=True)
            raise
    
    def _get_match_dir(self, match_id: str) -> str:
        """Get match directory path"""
        return os.path.join(self.base_dir, "matches", match_id)
    
    def get_match_data(self, match_id: str) -> Dict[str, Any]:
        """Get match data"""
        try:
            match_dir = self._get_match_dir(match_id)
            
            result = {}
            
            # Read match info
            try:
                with open(os.path.join(match_dir, "info.json"), 'r', encoding='utf-8') as f:
                    result['info'] = json.load(f)
            except FileNotFoundError:
                result['info'] = None
            
            # Read squads
            try:
                with open(os.path.join(match_dir, "squads.json"), 'r', encoding='utf-8') as f:
                    result['squads'] = json.load(f)
            except FileNotFoundError:
                result['squads'] = None
            
            # Try to read latest live data if available
            try:
                with open(os.path.join(match_dir, "live", "latest.json"), 'r', encoding='utf-8') as f:
                    result['live'] = json.load(f)
            except FileNotFoundError:
                result['live'] = None
            
            # Try to read latest scorecard if available
            try:
                with open(os.path.join(match_dir, "scorecard", "latest.json"), 'r', encoding='utf-8') as f:
                    result['scorecard'] = json.load(f)
            except FileNotFoundError:
                result['scorecard'] = None
            
            return result
        except Exception as e:
            logger.error(f"Failed to get data for match {match_id}: {str(e)}", exc_info=True)
            return {}
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            # Get match list
            matches = self.get_match_list()
            
            # Count matches by status
            status_counts = {
                "UPCOMING": 0,
                "LIVE": 0,
                "COMPLETED": 0
            }
            
            for match in matches:
                status = match.get('status', 'UNKNOWN')
                if status in status_counts:
                    status_counts[status] += 1
            
            # Calculate total storage used
            total_size = 0
            
            # Function to calculate directory size recursively
            def get_dir_size(path):
                total = 0
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
                return total
            
            # Calculate size of data directory
            if os.path.exists(self.base_dir):
                total_size = get_dir_size(self.base_dir)
            
            return {
                "total_matches": len(matches),
                "matches_by_status": status_counts,
                "total_storage_bytes": total_size,
                "total_storage_mb": round(total_size / (1024 * 1024), 2),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {str(e)}", exc_info=True)
            return {}