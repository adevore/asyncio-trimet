from . import util, error
from datetime import timedelta, datetime
import asyncio
import aiohttp


__all__ = ['nearby', 'LocationQuery', 'Location']


@asyncio.coroutine
def nearby(app_id, ...):
    params = {
        'appIDs': app_id,
    }
    url = SERVER_ROOT + "ws/V1/arrivals?" + params_encoded
    response = yield from aiohttp.request('GET', url)
    raw_data = yield from response.read()
    data = json.loads(raw_data.decode('utf8'))
    if 'errorMessage' in data['resultSet']:
        raise error.QueryError(data)
    return LocationQuery(data)


class LocationQuery:
    def __init__(self, data):
        pass


class Location:
    def __init__(self, data):
        pass