"""Model for TV program episode numbering handling."""

from typing import Any

from pydantic_xml import BaseXmlModel, attr


class TVProgramEpisodeNumber(BaseXmlModel, tag="episode-num", search_mode="ordered"):
    """Represents an episode number in a specific numbering system."""

    system: str = attr(name="system")
    """The numbering system used (e.g. "SxxExx", "xmltv_ns")."""

    raw_value: str
    """The raw episode number value as a string. Format depends on the numbering system."""

    @property
    def value(self) -> tuple[int | None, int | None]:
        """Parse the raw episode number into a (season, episode) tuple.

        :return: A tuple of (season, episode), where either (or both) can be None if not available.
        """
        return self.__value

    def __parse_value(self) -> tuple[int | None, int | None]:
        """Parse the raw_value based on the system. Used once after model initialization."""
        if self.system == "SxxExx" or self.system == "onscreen":
            val = self.raw_value.upper()

            # valid formats: S#E#, S#, E#
            if val.startswith("E"):
                # episode only format E##
                episode = int(val[1:])
                return (None, episode)

            # season+episode format S##E## or season only format S##
            (season, episode) = val.split("E")
            season = int(season[1:])
            episode = int(episode) if episode else None
            return (season, episode)

        if self.system == "xmltv_ns":
            # xmltv_ns format is '0.0.' for 'S1E1'
            # alternative format is '.0.' for episode only
            s, e, _ = self.raw_value.split(".")

            season = int(s) + 1 if s else None
            episode = int(e) + 1 if e else None
            return (season, episode)

        # cannot parse
        return (None, None)

    def model_post_init(self, __context: Any) -> None:
        """Hooks post-initialization to parse the raw value."""
        self.__value = self.__parse_value()
        return super().model_post_init(__context)
