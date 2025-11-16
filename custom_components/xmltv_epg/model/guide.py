"""Module defining the TVGuide model for XMLTV EPG data."""

from typing import Any

from pydantic_xml import BaseXmlModel, attr, element

from .channel import TVChannel
from .program import TVProgram


class TVGuide(BaseXmlModel, tag="tv", search_mode="ordered"):
    """Represents a TV Guide containing channels and their programs."""

    source_name: str | None = attr(name="source-info-name", default=None)
    """Name of the source that provided the epg data, if available."""

    source_url: str | None = attr(name="source-info-url", default=None)
    """URL of the source that provided the epg data, if available."""

    generator_name: str | None = attr(name="generator-info-name", default=None)
    """Name of the program that generated the xmltv data, if available."""

    generator_url: str | None = attr(name="generator-info-url", default=None)
    """URL of the program that generated the xmltv data, if available."""

    channels: list[TVChannel] = element(tag="channel", default_factory=list)
    """List of all TV channels defined in this guide."""

    programs: list[TVProgram] = element(tag="programme", default_factory=list)
    """List of all TV programs defined in this guide."""

    @property
    def name(self) -> str | None:
        """Get the name of the guide.

        :return: generator_name, source_name, or empty string, depending on availability

        :note fallback required, as seen in https://github.com/shadow578/homeassistant_xmltv-epg/issues/32
        """
        return self.generator_name or self.source_name

    @property
    def url(self) -> str | None:
        """Get the info URL for the guide.

        :return: generator_url, source_url, or None, depending on availability

        :note fallback required, as seen in https://github.com/shadow578/homeassistant_xmltv-epg/issues/32
        """
        return self.generator_url or self.source_url

    def model_post_init(self, __context: Any) -> None:
        """Hooks post-initialization to cross-link channels and programs."""
        for program in self.programs:
            channel = self.get_channel(program.channel_id)
            if channel is not None:
                channel._link_program(program)
                program._link_channel(channel)

    def get_channel(self, channel_id: str) -> TVChannel | None:
        """Get channel by ID."""
        return next((c for c in self.channels if c.id == channel_id), None)
