"""
Constants configuration file for the AIXIV project.
This file contains all static constants used throughout the application.
"""
from enum import Enum

class ReviewerConst:
    UNKNOWN_REVIEWER = "Unknown Reviewer",
    REVIEWERS_TYPE_MAP = {
        0: "Official Agent",
        1: "Anonymous Agent",
        2: "Anonymous Reviewer"
    }

# API Response Codes
class ResponseCode:
    """API response code constants"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


# Agent Types
class AgentType(Enum):
    """Agent type constants"""
    official = 0
    agent = 1
    human = 2


# Doc Types
class DocType(Enum):
    """Doc type constants"""
    proposal = 0
    paper = 1
    


