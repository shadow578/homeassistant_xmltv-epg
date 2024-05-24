"""Constants for testing."""
from datetime import datetime, timedelta

from custom_components.xmltv_epg.model import TVGuide, TVChannel, TVProgram

MOCK_NOW = datetime(2024, 5, 17, 12, 45, 0)


MOCK_TV_GUIDE_NAME = "MOCK XMLTV"
MOCK_TV_GUIDE_URL = "http://example.com/epg.xml"
MOCK_TV_GUIDE_URL_GZ = "http://example.com/epg.xml.gz"

def get_mock_tv_guide() -> TVGuide:
    """Build a TV Guide object.

    :return: TV Guide object with the following data:

    The TV Guide contains 3 channels with 2 programs each:
    - 'mock 1' (name='Mock Channel 1'):
      * 'CH 1 Current' from (MOCK_NOW - 15 minutes) to (MOCK_NOW + 15 minutes)
      * 'CH 1 Upcoming' from (MOCK_NOW + 15 minutes) to (MOCK_NOW + 45 minutes)
    - 'mock 2' (name='Mock Channel 2'):
      * 'CH 2 Current' from (MOCK_NOW - 15 minutes) to (MOCK_NOW + 15 minutes)
      * 'CH 2 Upcoming' from (MOCK_NOW + 15 minutes) to (MOCK_NOW + 45 minutes)
    - 'mock 3' (name='Mock Channel 3'):
      * 'CH 3 Current' from (MOCK_NOW - 15 minutes) to (MOCK_NOW + 15 minutes)
      * 'CH 3 Upcoming' from (MOCK_NOW + 15 minutes) to (MOCK_NOW + 45 minutes)

    All Programs have description="Description" set.

    CH 3 Current has episode="S1E1" and subtitle="Subtitle" set.
    CH 3 Upcoming has episode="S1E2" and subtitle="Subtitle" set.
    """
    guide = TVGuide(
        generator_name=MOCK_TV_GUIDE_NAME,
        generator_url=MOCK_TV_GUIDE_URL
    )

    channels = [
        TVChannel(id="mock 1", name="Mock Channel 1"),
        TVChannel(id="mock 2", name="Mock Channel 2"),
        TVChannel(id="mock 3", name="Mock Channel 3"),
    ]

    current_start = MOCK_NOW - timedelta(minutes=15)
    current_end = MOCK_NOW + timedelta(minutes=15)

    upcoming_start = MOCK_NOW + timedelta(minutes=15)
    upcoming_end = MOCK_NOW + timedelta(minutes=45)

    programs = [
        TVProgram(
            channel_id="mock 1",
            start=current_start,
            end=current_end,
            title="CH 1 Current",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 2",
            start=current_start,
            end=current_end,
            title="CH 2 Current",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 3",
            start=current_start,
            end=current_end,
            title="CH 3 Current",
            description="Description",
            episode="S1E1",
            subtitle="Subtitle",
        ),
        TVProgram(
            channel_id="mock 1",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 1 Upcoming",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 2",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 2 Upcoming",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 3",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 3 Upcoming",
            description="Description",
            episode="S1E2",
            subtitle="Subtitle",
        ),
    ]

    # cross-link programs with channels
    for program in programs:
        program.cross_link_channel(channels)

    guide.channels = channels
    guide.programs = programs
    return guide

MOCK_TV_GUIDE = get_mock_tv_guide()
