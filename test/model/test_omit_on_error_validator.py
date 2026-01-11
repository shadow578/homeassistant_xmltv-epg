"""Test cases for custom 'on error omit' validator."""

from pydantic_xml import BaseXmlModel, attr, element, xml_field_validator

from custom_components.xmltv_epg.model.omit_on_error_validator import (
    parse_list_omit_on_error,
)


def test_omit_on_error_validator():
    """Test omit on error validator utility."""

    class FooItem(BaseXmlModel, tag="item"):
        id: str = attr(name="id")
        value: str

    class Foo(BaseXmlModel, tag="list"):
        items: list[FooItem] = element(tag="item", default_factory=list)

        @xml_field_validator("items")
        @classmethod
        def _omit_invalid_items(cls, element, field_name) -> list:
            """Omit invalid items from items lists while parsing."""
            return parse_list_omit_on_error(element, FooItem, cls.__xml_search_mode__)

    foo = Foo.from_xml("""
<list>
  <item id="1">Item 1</item>
  <item id="2">Item 2</item>
  <item id="3"></item>       <!-- Missing value, should be omitted -->
  <item>Item 4</item>        <!-- Missing id attribute, should be omitted -->
</list>
""")

    assert len(foo.items) == 2

    assert foo.items[0].id == "1"
    assert foo.items[0].value == "Item 1"

    assert foo.items[1].id == "2"
    assert foo.items[1].value == "Item 2"
