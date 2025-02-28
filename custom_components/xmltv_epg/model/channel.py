"""TV Channel Model."""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import cast

from .helper import get_child_as_text, is_none_or_whitespace
from .program import TVProgram


class TVChannel:
    """TV Channel Class."""

    TAG = "channel"

    def __init__(self, id: str, name: str, icon_url: str | None = None):
        """Initialize TV Channel."""
        self.id = id
        self.name = name
        self.icon_url = icon_url

        self.programs: list[TVProgram] = []

    def add_program(self, program: TVProgram):
        """Add a program to channel."""
        self.programs.append(program)

        # keep programs sorted by start time
        self.programs.sort(key=lambda p: p.start)

    def get_current_program(self, time: datetime) -> TVProgram | None:
        """Get current program at given time."""
        for program in self.programs:
            if program.start.timestamp() <= time.timestamp() < program.end.timestamp():
                return program

        return None

    def get_next_program(self, time: datetime) -> TVProgram | None:
        """Get next program after given time."""
        for program in self.programs:
            if program.start.timestamp() >= time.timestamp():
                return program

        return None

    def get_last_program(self) -> TVProgram | None:
        """Get last program entry."""
        if len(self.programs) == 0:
            return None

        return self.programs[-1]

    @classmethod
    def from_xml(cls, xml: ET.Element) -> "TVChannel | None":
        """Initialize TV Channel from XML Node, if possible.

        :param xml: XML Node
        :return: TV Channel object, or None

        XML node format is:
        <channel id="DE: WDR Essen">
          <display-name>WDR Essen</display-name>
        </channel>
        """

        # node must be a channel
        if xml.tag != cls.TAG:
            return None

        # get id and display name
        id = xml.attrib.get("id")
        if is_none_or_whitespace(id):
            return None
        id = cast(str, id)

        name = get_child_as_text(xml, "display-name")
        if is_none_or_whitespace(name):
            return None
        name = cast(str, name)

        # remove 'XX: ' prefix from name, if present
        if len(name) > 4 and name[2] == ":" and name[3] == " ":  # 'XX: '
            name = name[4:]

        # get optional icon url
        icon = xml.find("icon")
        if icon is not None:
            icon = icon.attrib.get("src")

        return cls(id, name, icon)
