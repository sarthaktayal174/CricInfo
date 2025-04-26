from enum import Enum
from typing import Dict, List, Any, Optional

class MatchStatus(str, Enum):
    """Enum for match status"""
    UPCOMING = "UPCOMING"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"

class Match:
    """Class representing a cricket match"""
    id: str
    teams: str
    format: str
    dateTime: str
    url: str
    status: MatchStatus