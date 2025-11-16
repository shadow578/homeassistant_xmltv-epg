"""Constants for testing."""

from datetime import datetime, timedelta

from custom_components.xmltv_epg.model import (
    TVChannel,
    TVGuide,
    TVImage,
    TVProgram,
    TVProgramEpisodeNumber,
)

MOCK_NOW = datetime(2024, 5, 17, 12, 45, 0)


MOCK_TV_GUIDE_NAME = "MOCK XMLTV"
MOCK_TV_GUIDE_URL = "http://example.com/epg.xml"


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
    channels = [
        TVChannel(
            id="mock 1",
            name="Mock Channel 1",
            icon=TVImage(url="http://example.com/ch/mock1.jpg"),
        ),
        TVChannel(
            id="mock 2",
            name="Mock Channel 2",
            icon=TVImage(url="http://example.com/ch/mock2.jpg"),
        ),
        TVChannel(
            id="mock 3",
            name="Mock Channel 3",
            icon=TVImage(url="http://example.com/ch/mock3.jpg"),
        ),
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
            image=TVImage(url="http://example.com/pr/ch1_cur.jpg"),
        ),
        TVProgram(
            channel_id="mock 2",
            start=current_start,
            end=current_end,
            title="CH 2 Current",
            description="Description",
            image=TVImage(url="http://example.com/pr/ch2_cur.jpg"),
        ),
        TVProgram(
            channel_id="mock 3",
            start=current_start,
            end=current_end,
            title="CH 3 Current",
            description="Description",
            episode_raw=[
                TVProgramEpisodeNumber(system="onscreen", raw_value="S1E1"),
            ],
            subtitle="Subtitle",
            image=TVImage(url="http://example.com/pr/ch3_cur.jpg"),
        ),
        TVProgram(
            channel_id="mock 1",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 1 Upcoming",
            description="Description",
            image=TVImage(url="http://example.com/pr/ch1_upc.jpg"),
        ),
        TVProgram(
            channel_id="mock 2",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 2 Upcoming",
            description="Description",
            image=TVImage(url="http://example.com/pr/ch2_upc.jpg"),
        ),
        TVProgram(
            channel_id="mock 3",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 3 Upcoming",
            description="Description",
            episode_raw=[
                TVProgramEpisodeNumber(system="onscreen", raw_value="S1E2"),
            ],
            subtitle="Subtitle",
            image=TVImage(url="http://example.com/pr/ch3_upc.jpg"),
        ),
    ]

    return TVGuide(
        generator_name=MOCK_TV_GUIDE_NAME,
        generator_url=MOCK_TV_GUIDE_URL,
        channels=channels,
        programs=programs,
    )


MOCK_TV_GUIDE = get_mock_tv_guide()
