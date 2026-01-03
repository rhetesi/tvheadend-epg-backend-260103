import aiohttp
import async_timeout

class TVHHttpAPI:
    def __init__(self, host, port, username, password):
        self.base = f"http://{host}:{port}"
        self.auth = aiohttp.BasicAuth(username, password)

    async def get_epg(self):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            async with async_timeout.timeout(20):
                async with session.get(
                    f"{self.base}/api/epg/events/grid",
                    params={"limit": 1000},
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data.get("entries", [])

    async def record_event(self, event_id):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            async with async_timeout.timeout(10):
                async with session.post(
                    f"{self.base}/api/dvr/entry/create",
                    json={"event_id": event_id},
                ):
                    return True
