"""Model for TV program and channel images/icons."""

from pydantic_xml import BaseXmlModel, attr


class TVImage(BaseXmlModel, tag="icon", search_mode="ordered"):
    """Represents an image/icon associated with a TV program or channel."""

    url: str = attr(name="src")
    """The URL of the image."""

    width: int | None = attr(name="width", default=None)
    """The width of the image in pixels, if specified."""

    height: int | None = attr(name="height", default=None)
    """The height of the image in pixels, if specified."""
