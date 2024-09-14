"""Constants for assist satellite."""

from enum import IntFlag

DOMAIN = "assist_satellite"


class AssistSatelliteEntityFeature(IntFlag):
    """Supported features of Assist satellite entity."""

    ANNOUNCE = 1
    """Device supports remotely triggered announcements."""

    ANNOUNCE_RESPONSE = 2
    """Device supports responding to announcements."""
