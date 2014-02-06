"""
direction values
================

"""

import asyncio
import aiohttp
import urllib.parse
import json

from . import util, error

__all__ = [
    'fetch_arrivals',
    'ArrivalQuery',
    'Arrival',
    'Location',
    'Destination',
    'Position',
]


SERVER_ROOT = "http://developer.trimet.org/"


@asyncio.coroutine
def fetch_arrivals(app_id, *stops, streetcar=False):
    """
    Arguments
    =========
    
    app_id: Application ID (str)
    *stops: arbitrary number of stops (int|str)
    streetcar: Streetcar arrivals only (bool)
    """
    params = {
        'locIDs': ",".join(map(str, stops)),
        'appID': app_id,
        'json': "true",
        'streetcar': "true" if streetcar else "false",
        }
    params_encoded = urllib.parse.urlencode(params)
    url = SERVER_ROOT + "ws/V1/arrivals?" + params_encoded
    response = yield from aiohttp.request('GET', url)
    raw_data = yield from response.read()
    data = json.loads(raw_data.decode('utf8'))
    if 'errorMessage' in data['resultSet']:
        raise error.QueryError(data)
    return ArrivalQuery(data)


class ArrivalQuery:
    """
    Attributes
    ==========
    
    arrivals: ([Arrival])
    locations: ([Location])
    query_time: datetime.datetime
    
    """
    def __init__(self, data):
        result = data['resultSet']
        self.arrivals = list(map(Arrival, result.pop('arrival', [])))
        self.locations = list(map(Location, result.pop('location')))
        self.query_time = util.parse_trimet_time(result.pop('queryTime'))
    
    def for_route(self, route):
        return [a for a in self.arrivals if a.route == route]
    
    def for_location(self, location):
        if isinstance(location, Location):
            loc_id = location.location_id
        else:
            loc_id = location
        return [a for a in self.arrivals if a.location_id == loc_id]


class Arrival:
    """
    Attributes
    ==========

    block: 
    trip: list of major stops ([Destination])
    position: Position of bus (Position)
    departed: Has departed? (bool)
    detour: Is detoured? (bool)
    direction: Direction of travel (str)
    estimated: Estimate time of arrival (datetime.datetime or None)
    full_sign: Full sign (str)
    location_id: Stop number (int)
    piece: The piece of the block for the arrival (str)
    route: Route number (int)
    scheduled: Scheduled arrival time (datetime.datetime or None)
    short_sign: Short sign (str)
    status: (str)
        estimated: arrival time estimated with vehicle position
        scheduled: Only scheduled time available
        delayed: Status uncertain
        canceled: 

    """
    def __init__(self, data):
        self.block = data.pop('block')
        if 'blockPosition' in data:
            block_position = data.pop('blockPosition')
            self.trip = list(map(Destination, block_position.pop('trip')))
            self.position = Position(block_position)
        else:
            self.position = self.trip = None
        self.departed = data.pop('departed')
        self.detour = data.pop('detour')
        self.direction = data.pop('dir')
        if 'estimated' in data:
            self.estimated = util.parse_trimet_time(data.pop('estimated'))
        else:
            self.estimated = None
        self.full_sign = data.pop('fullSign')
        self.location_id = data.pop('locid')
        self.piece = data.pop('piece')
        self.route = data.pop('route')
        self.scheduled = util.parse_trimet_time(data.pop('scheduled'))
        self.short_sign = data.pop('shortSign')
        self.status = data.pop('status')
        assert len(data) == 0, "Some data points remain"

class Location:
    """
    Attributes
    ==========
    
    id: Location/Stop ID (int)
    description: Stop description
    direction: Direction (str)
    latitude: Latitude (float)
    longitude: Longitude (float)
    """
    def __init__(self, data):
        self.id = data.pop('locid')
        self.description = data.pop('desc')
        self.direction = data.pop('dir')
        self.latitude = data.pop('lat')
        self.longitude = data.pop('lng')
        assert len(data) == 0, "Some data points remain"


class Destination:
    """
    Attributes
    ==========
    
    description:
    remaining:
    direction:
    pattern:
    progress:
    route:
    trip_number:
    """
    def __init__(self, data):
        self.description = data.pop('desc')
        self.remaining = data.pop('destDist')
        self.direction = data.pop('dir')
        self.pattern = data.pop('pattern')
        self.progress = data.pop('progress')
        self.route = data.pop('route')
        self.trip_number = data.pop('tripNum')
        assert len(data) == 0, "Some data points remain"


class Position:
    """
    Attributes
    ==========
    
    feet: Number of feet the vehicle is from the spot (int)
    heading: No idea (int)
    latitude: Latitude of the vehicle (float)
    longitude: Longitude of the vehicle (float)
    timestamp: Time that the position was captured (datetime.datetime)
    """
    def __init__(self, data):
        self.feet = data.pop('feet')
        self.heading = data.pop('heading')
        self.latitude = data.pop('lat')
        self.longitude = data.pop('lng')
        self.timestamp = util.parse_trimet_time(data.pop('at'))
        assert len(data) == 0, "Some data points remain"


def main():
    import sys
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            query = ArrivalQuery(json.load(f))
    else:
        query = ArrivalQuery(json.load(sys.stdin))
    print(query)


if __name__ == '__main__':
    main()