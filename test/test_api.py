"""Test xmltv_epg api component."""

import gzip
import inspect
import io
import lzma
import zipfile
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.xmltv_epg.api import XMLTVClient

from .const import (
    MOCK_TV_GUIDE_NAME,
    MOCK_TV_GUIDE_URL,
)


async def create_zip_file(contents: list[tuple[str, str]]) -> bytes:
    """Create a zip file containing multiple files given in contents."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, content in contents:
            zip_file.writestr(file_name, content)

    return buffer.getvalue()


async def create_xml_zip_single(xml):
    """Prepare xml for test [xml file inside zip archive]."""
    return await create_zip_file([("tv_guide.xml", xml.decode())])


async def create_xml_zip_multi_file(xml):
    """Prepare xml for test [xml file inside zip archive, with additional files]."""
    return await create_zip_file([("license.txt", ""), ("tv_guide.xml", xml.decode())])


# the configuration profiles to test
# format is: "profile name": (url, content_type, content_encoding , compression_function)
TEST_CONFIGURATIONS = {
    # configurations for providers that can get their
    # content-type and content-encoding right:
    "plain xml, raw transfer": (
        MOCK_TV_GUIDE_URL,
        "application/xml",
        None,
        None,
    ),
    "plain xml, raw transfer, alternative content type": (
        MOCK_TV_GUIDE_URL,
        "text/xml",
        None,
        None,
    ),
    "plain xml, gzip transfer": (  # elres.de, xmltv.net, xmltvfr.fr
        MOCK_TV_GUIDE_URL,
        "application/xml",
        "gzip",
        None,  # auto-decompress by aiohttp
    ),
    "plain xml, gzip transfer, alternative content type": (  # xmltv.info
        MOCK_TV_GUIDE_URL,
        "text/xml",
        "gzip",
        None,  # auto-decompress by aiohttp
    ),
    "plain xml, xz transfer": (
        MOCK_TV_GUIDE_URL,
        "application/xml",
        "xz",
        None,  # auto-decompress by aiohttp (?)
    ),
    "plain xml, xz transfer, alternative content type": (  # xmltvfr.fr
        MOCK_TV_GUIDE_URL,
        "text/xml",
        "xz",
        None,  # auto-decompress by aiohttp (?)
    ),
    "gzipped xml, raw transfer": (
        MOCK_TV_GUIDE_URL + ".gz",
        "application/gzip",
        None,
        gzip.compress,
    ),
    "gzipped xml, raw transfer, alternative content type": (  # xmltvfr.fr
        MOCK_TV_GUIDE_URL + ".gz",
        "application/x-gzip",
        None,
        gzip.compress,
    ),
    "xz-compressed xml, raw transfer": (  # elres.de, xmltvfr.fr
        MOCK_TV_GUIDE_URL + ".xz",
        "application/x-xz",
        None,
        lzma.compress,
    ),
    "xml file inside zip archive": (  # xmltvfr.fr
        MOCK_TV_GUIDE_URL + ".zip",
        "application/zip",
        None,
        create_xml_zip_single,
    ),
    # additional configurations found in the wild, where providers
    # did not get their content-type and content-encoding right:
    "gzipped xml, gzip transfer (wrong content-type)": (  # elres.de
        MOCK_TV_GUIDE_URL + ".gz",
        "application/gzip",
        "gzip",
        None,  # auto-decompress by aiohttp
    ),
    "gzipped xml, gzip transfer (gzipped twice)": (
        MOCK_TV_GUIDE_URL + ".gz",
        "application/gzip",
        "gzip",
        gzip.compress,
    ),
    "gzipped xml (file download)": (  # unknown provider
        MOCK_TV_GUIDE_URL + ".gz",
        "application/octet-stream",
        None,
        gzip.compress,
    ),
    "xml file inside zip archive, with additional files": (
        MOCK_TV_GUIDE_URL + ".zip",
        "application/zip",
        None,
        create_xml_zip_multi_file,
    ),
}


def create_mock_session_for_get():
    """Create a mock session that supports get().

    :return: (session, response object)
    """

    response = AsyncMock()
    response.raise_for_status = MagicMock()

    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get = AsyncMock(return_value=response)

    return session, response


@pytest.mark.parametrize(
    ("url", "content_type", "content_encoding", "compression_function"),
    TEST_CONFIGURATIONS.values(),
    ids=TEST_CONFIGURATIONS.keys(),
)
async def test_xmltv_client_get_data(
    anyio_backend,
    url: str,
    content_type: str,
    content_encoding: str,
    compression_function: Callable | None,
):
    """Test XMLTVClient.async_get_data with variable configurations."""

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

    def get_header(name: str, default=None):
        """Get response header value mock."""
        if name == "Content-Encoding":
            return content_encoding
        elif name == "Content-Type":
            return content_type
        else:
            return default

    response.headers.get = get_header

    if compression_function:
        if inspect.iscoroutinefunction(compression_function):
            compressed_xml = await compression_function(xml.encode())
        else:
            compressed_xml = compression_function(xml.encode())

        response.read.return_value = compressed_xml
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
    assert guide.generator_url == url

    assert len(guide.channels) == 1
    assert guide.channels[0].id == "CH1"
