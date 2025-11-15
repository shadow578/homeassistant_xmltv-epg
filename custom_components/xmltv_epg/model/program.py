"""TV Program Model Definition."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from pydantic import field_validator
from pydantic_xml import BaseXmlModel, attr, element

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

    episode_raw: list[TVProgramEpisodeNumber] = element(
        tag="episode-num", default_factory=list
    )
    """List of episode numbers describing what episode of a series this program is.
    Multiple entries are likely to describe the same episode in different numbering systems.
    For normal use, the `episode` property should be used instead."""

    image: TVImage | None = element(tag="icon", default=None)
    """A Image / Icon associated with the program, if any.
    Generally, this will be a thumbnail or poster image."""

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_datetime(cls, value: str) -> datetime:
        """Parse datetime from XMLTV format.

        Example value "20240517124500 +0200" shall be parsed
        to datetime object for 17th May 2024, 12:45:00 UTC+2.
        """
        return datetime.strptime(value, "%Y%m%d%H%M%S %z")

    @property
    def episode(self) -> str | None:
        """Get the episode number as SxxExx string.

        If only either season or episode is available, returns E or S only.

        :return: SxxExx string, or None if not available
        """
        # find most complete episode number
        best = (None, None)
        best_score = 0
        for ep in self.episode_raw:
            (s, e) = ep.value
            score = 0
            if s is not None:
                score += 1
            if e is not None:
                score += 1

            if score > best_score:
                best = (s, e)
                best_score = score

            if score == 2:
                # best possible score reached
                break

        (s, e) = best
        if s is None and e is None:
            return None

        s = f"S{s:02d}" if s is not None else ""
        e = f"E{e:02d}" if e is not None else ""
        return f"{s}{e}"

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
