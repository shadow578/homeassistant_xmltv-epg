"""Module providing validator utilities to omit items from lists on parsing errors."""

import contextlib
from typing import TypeVar

from pydantic_core import ValidationError
from pydantic_xml import BaseXmlModel
from pydantic_xml.element.element import SearchMode, XmlElementReader

TModel = TypeVar("TModel", bound=BaseXmlModel)


def parse_list_omit_on_error(
    element: XmlElementReader,
    model: type[TModel],
    search_mode: SearchMode,
) -> list[TModel]:
    """Parse a homogeneous list of items, omitting all items that fail validation.

    Example usage:
    .. code-block:: python
     class Foo(BaseXmlModel, tag="foo", search_mode="ordered"):
       items: list[FooItem] = element(tag="item", default_factory=list)

       @xml_field_validator("items")
       @classmethod
       def _omit_invalid_items(cls, element: XmlElementReader, field_name: str) -> list:
         return parse_list_omit_on_error(element, FooItem, cls.__xml_search_mode__)

    :param element: Input XML element reader.
    :param model: Model type of the list items.
    :param search_mode: Search mode to use when looking for child elements.
    :return: List of valid items.
    """
    # Create snapshot to avoid modifying the original element
    # this could cause other validators to miss elements
    element = element.create_snapshot()

    # validate model tag is set
    tag = model.__xml_tag__
    if tag is None:
        raise ValueError("Tag must be provided if model has no xml tag defined.")

    # Iterate over all elements, collecting only valid ones
    items = []
    while True:
        child = element.pop_element(tag=tag, search_mode=search_mode)
        if child is None:
            break

        with contextlib.suppress(ValidationError):
            items.append(model.from_xml_tree(child.to_native()))

    return items
