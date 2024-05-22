"""TVXML Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

import xml.etree.ElementTree as ET

from .tvxml.model import TVGuide
import gzip

class TVXMLClientError(Exception):
    """Exception to indicate a general API error."""

class TVXMLClientCommunicationError(
    TVXMLClientError
):
    """Exception to indicate a communication error."""


class TVXMLClient:
    """TVXML Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> None:
        """TVXML Client."""
        self._session = session
        self._url = url

    async def async_get_data(self) -> TVGuide:
        """Fetch TVXML Guide data."""
        try:
            async with async_timeout.timeout(10):
                # fetch data
                response = await self._session.request(
                    method="GET",
                    url=self._url,
                )
                response.raise_for_status()

                if response.content_type == "text/xml":
                    # raw XML text, read as-is
                    data = await response.text()

                elif response.content_type == "application/gzip" or "xml.gz" in str(response.url):
                    # xml.gz file, read as binary and decompress
                    gzipped_data = await response.read()

                    # decompress the gzipped data
                    data = gzip.decompress(gzipped_data).decode()

                else:
                    raise TVXMLClientError(
                        f"Don't know how to handle content type '{response.content_type}' (from {response.url})",
                    )

                # parse XML data
                xml = ET.fromstring(data)

                guide = TVGuide.from_xml(xml)
                if guide is None:
                    raise TVXMLClientError(
                        "Failed to parse TV Guide data",
                    )

                return guide
        except TVXMLClientError as exception:
            raise exception
        except asyncio.TimeoutError as exception:
            raise TVXMLClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise TVXMLClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise TVXMLClientError(
                "Something really wrong happened!"
            ) from exception
