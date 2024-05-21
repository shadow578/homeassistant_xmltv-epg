"""Constants for tvxml_epg."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "TVXML EPG"
DOMAIN = "tvxml_epg"
VERSION = "0.0.0"

OPT_UPDATE_INTERVAL = "update_interval_hours"
DEFAULT_UPDATE_INTERVAL = 12 # hours

OPT_PROGRAM_LOOKAHEAD = "program_lookahead_minutes"
DEFAULT_PROGRAM_LOOKAHEAD = 15 # minutes
