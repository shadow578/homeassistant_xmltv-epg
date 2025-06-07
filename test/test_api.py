"""Test xmltv_epg api component."""

import gzip
import lzma
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.xmltv_epg.api import XMLTVClient

from .const import (
    MOCK_TV_GUIDE_NAME,
    MOCK_TV_GUIDE_URL,
)

# the configuration profiles to test
# format is: "profile name": (url, content_type, compression_function)
TEST_CONFIGURATIONS = {
    "plain xml with application/xml": (
        MOCK_TV_GUIDE_URL,
        "application/xml",
        None,
    ),
    "plain xml with test/xml": (
        MOCK_TV_GUIDE_URL,
        "text/xml",
        None,
    ),
    "gzipped xml with application/gzip": (
        MOCK_TV_GUIDE_URL + ".gz",
        "application/gzip",
        gzip.compress,
    ),
    "gzipped xml with appliation/octet-stream": (
        MOCK_TV_GUIDE_URL + ".gz",
        "application/octet-stream",
        gzip.compress,
    ),
    "xz-compressed xml with application/x-xz": (
        MOCK_TV_GUIDE_URL + ".xz",
        "application/x-xz",
        lzma.compress,
    ),
}


def create_mock_session_for_get():
    """Create a mock session that supports get().

    :return: (mock session, mock response)
    """

    response = AsyncMock()
    response.raise_for_status = MagicMock()

    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get = AsyncMock(return_value=response)

    return session, response


@pytest.mark.parametrize(
    ("url", "content_type", "compression_function"),
    TEST_CONFIGURATIONS.values(),
    ids=TEST_CONFIGURATIONS.keys(),
)
async def test_xmltv_client_get_data_(
    anyio_backend, url: str, content_type: str, compression_function: Callable | None
):
    """Test XMLTVClient.async_get_data with GZIP response and correct content_type."""

    # prepare the session and response
    session, response = create_mock_session_for_get()

    xml = f"""
<tv generator-info-name="{MOCK_TV_GUIDE_NAME}" generator-info-url="{url}">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
"""

    response.url = url
    response.content_type = content_type

    if compression_function:
        response.read.return_value = compression_function(xml.encode())
    else:
        response.text.return_value = xml

    # create client
    client = XMLTVClient(
        session=session,
        url=url,
    )

    # fetch data
    guide = await client.async_get_data()

    # check the guide
    assert guide
    assert guide.generator_name == MOCK_TV_GUIDE_NAME
    assert guide.generator_url == MOCK_TV_GUIDE_URL

    assert len(guide.channels) == 1
    assert guide.channels[0].id == "CH1"
