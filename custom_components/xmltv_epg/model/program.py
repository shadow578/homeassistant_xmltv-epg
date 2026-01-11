"""TV Program Model Definition."""

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from pydantic import field_validator
from pydantic_xml import BaseXmlModel, attr, element, xml_field_validator

from custom_components.xmltv_epg.model.omit_on_error_validator import (
    parse_list_omit_on_error,
)

from .category import TVProgramCategory
from .episode_number import TVProgramEpisodeNumber
from .image import TVImage

if TYPE_CHECKING:
    from .channel import TVChannel


class TVProgram(BaseXmlModel, tag="programme", search_mode="ordered"):
    """Represents a TV Program at a specific time on a specific channel."""

    channel_id: str = attr(name="channel")
    """The channel ID the program is broadcasted on."""

    start: datetime = attr(name="start")
    """The time the program starts."""

    end: datetime = attr(name="stop")
    """The time the program ends."""

    title: str = element(tag="title")
    """The title of the program."""

    subtitle: str | None = element(tag="sub-title", default=None)
    """The subtitle of the program, if any."""

    description: str | None = element(tag="desc", default=None)
    """A description of the program's contents (e.g. synopsis), if any."""

    release_date: date | None = element(tag="date", default=None)
    """The release date of the program, if any."""

    language: str | None = element(tag="language", default=None)
    """The language of the program, if specified.
    Note that this is the display name of the language, not a language code."""

    episode_raw: list[TVProgramEpisodeNumber] = element(
        tag="episode-num", default_factory=list
    )
    """List of episode numbers describing what episode of a series this program is.
    Multiple entries are likely to describe the same episode in different numbering systems.
    For normal use, the `episode` property should be used instead."""

    categories: list[TVProgramCategory] = element(tag="category", default_factory=list)
    """List of categories / genres assigned to this program.
    Each category entry may specify a language."""

    image: TVImage | None = element(tag="icon", default=None)
    """A Image / Icon associated with the program, if any.
    Generally, this will be a thumbnail or poster image."""

    @xml_field_validator("episode_raw")
    @classmethod
    def _omit_invalid_episodes(cls, element, field_name) -> list:
        """Omit invalid items from episodes while parsing."""
        return parse_list_omit_on_error(
            element, TVProgramEpisodeNumber, cls.__xml_search_mode__
        )

    @xml_field_validator("categories")
    @classmethod
    def _omit_invalid_categories(cls, element, field_name) -> list:
        """Omit invalid items from categories while parsing."""
        return parse_list_omit_on_error(
            element, TVProgramCategory, cls.__xml_search_mode__
        )

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_datetime(cls, value: str) -> datetime:
        """Parse datetime from XMLTV format.

        Example value "20240517124500 +0200" shall be parsed
        to datetime object for 17th May 2024, 12:45:00 UTC+2.
        """
        if isinstance(value, datetime):
            return value

        return datetime.strptime(value, "%Y%m%d%H%M%S %z")

    @field_validator("release_date", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> date:
        """Parse date from XMLTV format.

        Example value "20200101" shall be parsed to date object for 1st Jan 2020.
        """
        if isinstance(value, date):
            return value

        value = value.strip()

        if len(value) == 8:  # YYYYMMDD
            return datetime.strptime(value, "%Y%m%d").date()
        elif len(value) == 6:  # YYYYMM
            return datetime.strptime(value, "%Y%m").date()
        elif len(value) == 4:  # YYYY
            return datetime.strptime(value, "%Y").date()
        else:
            raise ValueError(f"Invalid date format: {value}")

    def model_post_init(self, __context: Any) -> None:
        """Hooks post-initialization to validate start < end time."""
        if self.start >= self.end:
            raise ValueError("Program start time must be before end time")

        return super().model_post_init(__context)

    @property
    def episode(self) -> str | None:
        """Get the episode number as onscreen formatted string (via TVProgramEpisodeNumber::value_onscreen)."""
        best = None
        best_score = 0
        for ep in self.episode_raw:
            (s, e) = ep.value
            score = 0
            if s is not None:
                score += 1
            if e is not None:
                score += 1

            if score > best_score:
                best = ep
                best_score = score

            if score == 2:
                # best possible score reached
                break

        if best is None:
            return None
        return best.value_onscreen

    @property
    def duration(self) -> timedelta:
        """How long the program lasts."""
        return self.end - self.start

    @property
    def full_title(self) -> str:
        """Get the full title, including episode and / or subtitle, if available.

        :Examples:
        (1)
        Title: 'Program 1'
        Episode: None
        Subtitle: None
        Result: 'Program 1'

        (2)
        Title: 'Program 1'
        Episode: 'S1 E1'
        Subtitle: None
        Result: 'Program 1 (S1 E1)'

        (3)
        Title: 'Program 1'
        Episode: 'S1 E1'
        Subtitle: 'Subtitle 1'
        Result: 'Program 1 - Subtitle 1 (S1 E1)'

        (4)
        Title: 'Program 1'
        Episode: None
        Subtitle: 'Subtitle 1'
        Result: 'Program 1 - Subtitle 1'

        """
        title = self.title

        if self.subtitle is not None and self.subtitle.strip() != "":
            title += f" - {self.subtitle}"

        episode = self.episode
        if episode is not None and episode.strip() != "":
            title += f" ({episode})"

        return title

    @property
    def channel(self) -> "TVChannel | None":
        """The channel object this program is broadcast on."""
        if not hasattr(self, "_TVProgram__channel"):
            # _link_channel was not called, fail silently
            return None

        return self.__channel

    def _link_channel(self, channel: "TVChannel"):
        """Set the channel object for this program.

        This method is internal and should not be called under normal circumstances.
        Cross-linking is handled by TVGuide.

        :param channel: Channel to link to this program.
        """
        self.__channel = channel
