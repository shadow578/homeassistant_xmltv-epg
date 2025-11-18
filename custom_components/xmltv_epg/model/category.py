"""Model for TV Program Category handling."""

from pydantic_xml import BaseXmlModel, attr


class TVProgramCategory(BaseXmlModel, tag="category", search_mode="ordered"):
    """Represents a TV Program Category."""

    language: str | None = attr(name="lang", default=None)
    """The language code the category name is in, if specified.
    Note that this is a language code (e.g. "en", "de-DE")."""

    name: str
    """The display name of the category, in the language specified."""
