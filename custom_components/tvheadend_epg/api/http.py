import logging
from typing import Any

import aiohttp
import async_timeout
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)


class TVHHttpApi:
    """HTTP API client for TVHeadend."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """
        base_url example:
            http://lando07.ddns.net:9981
            http://192.168.1.82:9981
        """
        self._base_url = base_url.rstrip("/")
        self._auth = aiohttp.BasicAuth(username, password)

    async def get_epg(self, limit: int = 1000) -> Any:
        """
        Fetch EPG data from TVHeadend via HTTP API.
        """
        endpoint = f"api/epg/events/grid?limit={limit}"
        url = urljoin(self._base_url + "/", endpoint)

        _LOGGER.debug("TVHeadend HTTP EPG request URL: %s", url)
        _LOGGER.debug("TVHeadend HTTP EPG user: %s", self._auth.login)

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with async_timeout.timeout(15):
                    async with session.get(url, auth=self._auth) as response:
                        if response.status == 401:
                            raise TVHHttpAuthError(
                                "Authentication failed (401). "
                                "Check TVHeadend username/password and API access."
                            )

                        response.raise_for_status()
                        return await response.json()

            except aiohttp.ClientConnectorError as err:
                raise TVHHttpConnectionError(
                    f"Cannot connect to TVHeadend at {self._base_url}"
                ) from err

            except aiohttp.ClientResponseError as err:
                raise TVHHttpRequestError(
                    f"HTTP error from TVHeadend: {err.status} {err.message}"
                ) from err

            except Exception:
                raise


class TVHHttpError(Exception):
    """Base class for TVHeadend HTTP errors."""


class TVHHttpAuthError(TVHHttpError):
    """Authentication error (401)."""


class TVHHttpConnectionError(TVHHttpError):
    """Connection error."""


class TVHHttpRequestError(TVHHttpError):
    """Other HTTP errors."""
