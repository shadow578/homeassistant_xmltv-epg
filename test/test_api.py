"""Test xmltv_epg api component."""
import aiohttp
import gzip

from unittest.mock import MagicMock, AsyncMock

from custom_components.xmltv_epg.api import XMLTVClient

from .const import MOCK_TV_GUIDE_NAME, MOCK_TV_GUIDE_URL, MOCK_TV_GUIDE_URL_GZ

def create_mock_session_for_get():
    """Create a mock session that supports get().

    :return: (mock session, mock response)
    """

    response = AsyncMock()
    response.raise_for_status = MagicMock()

    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get = AsyncMock(return_value=response)

    return session, response


async def test_xmltv_client_get_data_plain(
        anyio_backend
    ):
    """Test XMLTVClient.async_get_data with plain XML response."""

    # prepare the session and response
    session, response = create_mock_session_for_get()

    response.content_type = "text/xml"
    response.url = MOCK_TV_GUIDE_URL
    response.text.return_value = f"""
<tv generator-info-name="{MOCK_TV_GUIDE_NAME}" generator-info-url="{MOCK_TV_GUIDE_URL}">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
"""

    # create client
    client = XMLTVClient(
        session=session,
        url=MOCK_TV_GUIDE_URL,
    )

    # fetch data
    guide = await client.async_get_data()

    # check the guide
    assert guide
    assert guide.generator_name == MOCK_TV_GUIDE_NAME
    assert guide.generator_url == MOCK_TV_GUIDE_URL

    assert len(guide.channels) == 1
    assert guide.channels[0].id == "CH1"

async def test_xmltv_client_get_data_gzip_correct_content_type(
        anyio_backend
    ):
    """Test XMLTVClient.async_get_data with GZIP response and correct content_type."""

    # prepare the session and response
    session, response = create_mock_session_for_get()

    response.content_type = "application/gzip"
    response.url = MOCK_TV_GUIDE_URL_GZ
    response.read.return_value = gzip.compress(f"""
<tv generator-info-name="{MOCK_TV_GUIDE_NAME}" generator-info-url="{MOCK_TV_GUIDE_URL}">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
""".encode())

    # create client
    client = XMLTVClient(
        session=session,
        url=MOCK_TV_GUIDE_URL_GZ,
    )

    # fetch data
    guide = await client.async_get_data()

    # check the guide
    assert guide
    assert guide.generator_name == MOCK_TV_GUIDE_NAME
    assert guide.generator_url == MOCK_TV_GUIDE_URL

    assert len(guide.channels) == 1
    assert guide.channels[0].id == "CH1"

async def test_xmltv_client_get_data_gzip_wrong_content_type(
        anyio_backend
    ):
    """Test XMLTVClient.async_get_data with GZIP response and wrong content_type."""

    # prepare the session and response
    session, response = create_mock_session_for_get()

    response.content_type = "application/octet-stream"
    response.url = MOCK_TV_GUIDE_URL_GZ
    response.read.return_value = gzip.compress(f"""
<tv generator-info-name="{MOCK_TV_GUIDE_NAME}" generator-info-url="{MOCK_TV_GUIDE_URL}">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
""".encode())

    # create client
    client = XMLTVClient(
        session=session,
        url=MOCK_TV_GUIDE_URL_GZ,
    )

    # fetch data
    guide = await client.async_get_data()

    # check the guide
    assert guide
    assert guide.generator_name == MOCK_TV_GUIDE_NAME
    assert guide.generator_url == MOCK_TV_GUIDE_URL

    assert len(guide.channels) == 1
    assert guide.channels[0].id == "CH1"
