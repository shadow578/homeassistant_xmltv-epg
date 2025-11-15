"""TV Channel Model Definition."""

from datetime import datetime
from typing import Any

from pydantic_xml import BaseXmlModel, attr, element

from .image import TVImage
from .program import TVProgram


class TVChannel(BaseXmlModel, tag="channel", search_mode="ordered"):
    """Represents a TV Channel with its associated programs."""

    id: str = attr(name="id")
    """Unique ID of this channel."""

    name: str = element(tag="display-name")
    """Display name of this channel."""

    icon: TVImage | None = element(tag="icon", default=None)
    """Icon associated with this channel, if any.
    Generally, this will be a logo or similar image."""

    def model_post_init(self, __context: Any) -> None:
        """Hooks post-initialization to initialize programs field."""
        self.__programs: list[TVProgram] = []
        return super().model_post_init(__context)

    def _link_program(self, program: TVProgram):
        """Link a program to this channel.

        This method is internal and should not be called under normal circumstances.
        Cross-linking is handled by TVGuide.

        :param program: Program to link to this channel.
        """
        self.__programs.append(program)

        # ensure programs remain sorted by start time
        self.__programs.sort(key=lambda p: p.start)

    def get_current_program(self, time: datetime) -> TVProgram | None:
        """Get current program at given time."""
        for program in self.__programs:
            if program.start.timestamp() <= time.timestamp() < program.end.timestamp():
                return program

        return None

    def get_next_program(self, time: datetime) -> TVProgram | None:
        """Get next program after given time."""
        for program in self.__programs:
            if program.start.timestamp() >= time.timestamp():
                return program

        return None

    @property
    def last_program(self) -> TVProgram | None:
        """Last program entry by start time."""
        if len(self.__programs) == 0:
            return None

        return self.__programs[-1]
