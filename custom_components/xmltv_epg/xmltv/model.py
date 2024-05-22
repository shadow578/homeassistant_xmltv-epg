"""XMLTV Model Classes & Parsing."""

from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def is_none_or_whitespace(s: str) -> bool:
    """Check if string is None, empty, or whitespace."""
    return s is None or not isinstance(s, str) or len(s.strip()) == 0

def get_child_as_text(parent: ET.Element, tag: str) -> str:
    """Get child node text as string, or None if not found."""
    node = parent.find(tag)
    return node.text if node is not None else None

class TVChannel:
    """TV Channel Class."""

    TAG = 'channel'

    def __init__(self, id: str, name: str):
        """Initialize TV Channel."""
        self.id = id
        self.name = name
        self.programs = []

    def add_program(self, program: 'TVProgram'):
        """Add a program to channel."""
        self.programs.append(program)

        # keep programs sorted by start time
        self.programs.sort(key=lambda p: p.start)

    def get_current_program(self, time: datetime) -> 'TVProgram':
        """Get current program at given time."""
        for program in self.programs:
            if program.start.timestamp() <= time.timestamp() < program.end.timestamp():
                return program

        return None

    def get_next_program(self, time: datetime) -> 'TVProgram':
        """Get next program after given time."""
        for program in self.programs:
            if program.start.timestamp() >= time.timestamp():
                return program

        return None

    @classmethod
    def from_xml(cls, xml: ET.Element) -> 'TVChannel':
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
        id = xml.attrib.get('id')
        if is_none_or_whitespace(id):
            return None

        name = get_child_as_text(xml, 'display-name')
        if is_none_or_whitespace(name):
            return None

        # remove 'XX: ' prefix from name, if present
        if len(name) > 4 and name[2] == ':' and name[3] == ' ': # 'XX: '
            name = name[4:]

        return cls(id, name)

class TVProgram:
    """TV Program Class."""

    TAG = 'programme'

    def __init__(self,
                 channel_id: str,
                 start: datetime,
                 end: datetime,
                 title: str,
                 description: str,
                 episode: str = None,
                 subtitle: str = None):
        """Initialize TV Program."""
        if end <= start:
            raise ValueError('End time must be after start time.')

        self._channel_id = channel_id
        self.start = start
        self.end = end
        self.title = title
        self.description = description
        self.episode = episode
        self.subtitle = subtitle

        self.channel = None

    def cross_link_channel(self, channels: list[TVChannel]):
        """Set channel for program and cross-link.

        :param channels: List of TV Channels
        """
        # find channel by id
        channel = next((c for c in channels if c.id == self._channel_id), None)
        if channel is None:
            raise ValueError(f'Channel with ID "{self._channel_id}" not found.')

        # cross-link
        self.channel = channel
        self.channel.add_program(self)

    @property
    def duration(self) -> timedelta:
        """Get program duration."""
        return self.end - self.start

    @property
    def full_title(self) -> str:
        """Get the full title, including episode and / or subtitle, if available.

        Examples:
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

        if not is_none_or_whitespace(self.subtitle):
            title += f' - {self.subtitle}'

        if not is_none_or_whitespace(self.episode):
            title += f' ({self.episode})'

        return title


    @classmethod
    def from_xml(cls, xml: ET.Element) -> 'TVProgram':
        """Initialize TV Program from XML Node, if possible.

        Cross-link is not done here, call cross_link_channel() after all programs are created.

        :param xml: XML Node
        :return: TV Program object, or None

        XML node format is:
        <programme start="20240517124500 +0200" stop="20240517130000 +0200" channel="DE: WDR Essen">
          <title>WDR aktuell</title>
          <sub-title>vom 17.05.2024, 12:45 Uhr</sub-title>
          <desc>Das Sendung bietet Nachrichten für und aus Nordrhein-Westfalen im Magazinformat.</desc>
          <episode-num system="onscreen">S5 E34</episode-num>
        </programme>
        """

        # node must be a program
        if xml.tag != cls.TAG:
            return None

        # get start and end times
        start = xml.attrib.get('start')
        end = xml.attrib.get('stop')
        if is_none_or_whitespace(start) or is_none_or_whitespace(end):
            return None

        # parse start and end times
        try:
            start = datetime.strptime(start, '%Y%m%d%H%M%S %z')
            end = datetime.strptime(end, '%Y%m%d%H%M%S %z')
        except ValueError:
            return None

        # get channel id
        channel_id = xml.attrib.get('channel')
        if is_none_or_whitespace(channel_id):
            return None

        # get and validate program info
        title = get_child_as_text(xml, 'title')
        description = get_child_as_text(xml, 'desc')
        episode = get_child_as_text(xml, 'episode-num')
        subtitle = get_child_as_text(xml, 'sub-title')

        if is_none_or_whitespace(title) or is_none_or_whitespace(description):
            return None

        try:
            return cls(channel_id, start, end, title, description, episode, subtitle)
        except ValueError:
            return None

class TVGuide:
    """TV Guide Class."""

    TAG = 'tv'

    def __init__(self, generator_name: str = None, generator_url: str = None):
        """Initialize TV Guide."""
        self.generator_name = generator_name
        self.generator_url = generator_url

        self.channels = []
        self.programs = []

    def get_channel(self, channel_id: str) -> TVChannel:
        """Get channel by ID."""
        return next((c for c in self.channels if c.id == channel_id), None)

    @classmethod
    def from_xml(cls, xml: ET.Element) -> 'TVGuide':
        """Initialize TV Guide from XML Node, if possible.

        :param xml: XML Node
        :return: TV Guide object, or None

        XML node format is:
        <tv generator-info-name="Example" generator-info-url="https://example.com">
          <channel ... />
          <programme ... />
        </tv>
        """

        # node must be a TV guide
        if xml.tag != cls.TAG:
            return None

        # parse generator info
        generator_name = xml.attrib.get('generator-info-name')
        generator_url = xml.attrib.get('generator-info-url')

        # create guide instance
        guide = cls(generator_name, generator_url)

        # parse channels and programs
        for child in xml:
            if child.tag == TVChannel.TAG:
                channel = TVChannel.from_xml(child)
                if channel is not None:
                    # ensure no duplicate channel ids
                    if guide.get_channel(channel.id) is None:
                        guide.channels.append(channel)
                    else:
                        # ?!
                        continue
            elif child.tag == TVProgram.TAG:
                program = TVProgram.from_xml(child)
                if program is not None:
                    guide.programs.append(program)
            else:
                # ?!
                continue

        # cross-link programs with channels
        for program in guide.programs:
            program.cross_link_channel(guide.channels)

        return guide
