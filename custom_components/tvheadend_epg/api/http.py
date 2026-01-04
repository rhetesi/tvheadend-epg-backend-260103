import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientResponseError

_LOGGER = logging.getLogger(__name__)


class TVHHttpAuthError(Exception):
    """Authentication error."""


class TVHHttpConnectionError(Exception):
    """Connection error."""


class TVHHttpRequestError(Exception):
    """Request error."""


class TVHHttpApi:
    """HTTP API client for TVHeadend."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = aiohttp.ClientTimeout(total=20)

    async def _request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self._base_url}{path}"

        # ---- DIGEST AUTH FIRST (TVHeadend default) ----
        digest_auth = aiohttp.DigestAuth(self._username, self._password)

        try:
            async with aiohttp.ClientSession(
                auth=digest_auth,
                timeout=self._timeout,
            ) as session:
                async with session.get(url, params=params) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        except ClientResponseError as err:
            if err.status == 401:
                _LOGGER.debug("Digest auth failed, trying Basic auth fallback")
            else:
                raise

        except ClientError:
            pass

        # ---- BASIC AUTH FALLBACK ----
        basic_auth = aiohttp.BasicAuth(self._username, self._password)

        try:
            async with aiohttp.ClientSession(
                auth=basic_auth,
                timeout=self._timeout,
            ) as session:
                async with session.get(url, params=params) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        except ClientResponseError as err:
            if err.status == 401:
                raise TVHHttpAuthError("Invalid username or password") from err
            raise TVHHttpRequestError(err) from err

        except asyncio.TimeoutError as err:
            raise TVHHttpConnectionError("Connection timed out") from err

        except ClientError as err:
            raise TVHHttpConnectionError(err) from err

    async def get_epg(self, limit: int = 1000) -> list[dict[str, Any]]:
        """Fetch EPG data."""
        data = await self._request(
            "/api/epg/events/grid",
            params={"limit": limit},
        )
        return data.get("entries", [])
