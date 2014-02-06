from datetime import timedelta, datetime
import asyncio
import aiohttp
import json
from urllib.parse import urlencode

from .util import parse_trimet_time
from .error import QueryError


@asyncio.coroutine
def fetch_vehicles(app_id, routes=None, blocks=None, ids=None, since=None,
                bbox=None, non_revenue=False, on_route_only=True,
                show_stale=False):
    """
    routes: list of route numbers (str or int)
    blocks: list of block numbers (str or int)
    ids: list of vehicle numbers
    since: time in seconds or a datetime object
    bbox: (long min, lat min, long max, lat max) tuple
    non_revenue: bool, include vehicles on dead head routes

    returns VehicleLocationQuery
    """
    params = {}
    # routes
    if routes is not None:
        params['routes'] = ",".join(map(str, routes))
    # blocks
    if blocks is not None:
        params['blocks'] = ",".join(blocks)
    # ids
    if ids is not None:
        params['ids'] = ",".join(ids)
    # since
    if since is None:
        pass
    elif isinstance(since, int):
        params['since'] = str(since * 1000)
    elif isinstance(since, datetime):
        params['since'] = str(int(since.timestamp()) * 1000)
    # bbox
    if bbox:
        assert(len(bbox) == 4)
        params['bbox'] = ",".join(bbox)
    # non_revenue
    if non_revenue:
        params['showNonRevenue'] = "true"
    # on_route_only
    if not on_route_only:
        params['onRouteOnly'] = "false"
    # show_stale
    if show_stale:
        params['showStale'] = "true"
    url_base = "http://developer.trimet.org/beta/v2/vehicles?"
    url = url_base + urlencode(params)
    response = yield from aiohttp.request('GET', url)
    raw_data = yield from response.read()
    data = json.loads(raw_data)
    if 'errorMessage' in data['resultSet']:
        raise QueryError(data)
    return VehicleLocationQuery(data)


class VehicleLocationQuery:
    """
    Attributes
    ==========

    vehicles: List of vehicles ([Vehicle])
    query_time: Query timestamp (datetime.datetime)
    """
    def __init__(self, data):
        result = data['resultSet']
        self.vehicles = list(map(Vehicle, result.pop('vehicle', [])))
        self.query_time = parse_trimet_time(result.pop('queryTime'))
        assert len(data) == 0, "Data from query remains"


class Vehicle:
    """
    id: Vehicle ID (int)
    type:
    block_id: (int)
    bearing:
    service_date:
    location_in_schedule_day: Time relative to day (datetime.timedelta)
    time: ?
    expires: Expiration time of reading (datetime.datetime)
    longitude: Longitude (float)
    latitude: Latitude (float)
    route: Route number (int)
    direction: Direction (str)
    trip_id: Unique ID for this trip (int)
    delay: Delative amount
        TODO: description
    rail_track_id: Rail track, if applicable
    message_code: Not sure
    long_sign: Full sign message (str)
    short_sign: Short sign message (str)
    next_location_id: Next stop ID (int)
    next_stop_seq: TODO
    last_location_id: TODO
    last_stop_seq: TODO
    garage: TODO
    extra_trip_id: TODO
    extra_block_id: TODO
    vehicle_load: Unimplemented
    off_route: Unimplemented
    in_congestion: Unimplemented
    """
    
    def __init__(self, data):
        self.id = data.pop('vehicleID')
        self.type = data.pop('type')
        self.block_id = data.pop('blockID')
        self.bearing = data.pop('bearing')
        # Trimet gives seconds since epoch * 1000
        self.service_date = data.pop('serviceDate') // 1000
        lisd = timedelta(seconds=data.pop('locationInScheduleDay'))
        self.location_in_schedule_day = lisd
        self.time = parse_trimet_time(data.pop('time'))
        self.expires = parse_trimet_time(data.pop('expires'))
        self.longitude = data.pop('longitude')
        self.latitude = data.pop('latitude')
        self.route = data.pop('routeNumber')
        self.direction = data.pop('direction')
        self.trip_id = data.pop('tripID')
        self.delay = data.pop('delay')
        self.rail_track_id = data.pop('railTrackID')
        self.message_code = data.pop('messageCode')
        # Renamed to be consistent with Arrival interface
        self.long_sign = data.pop('signMessageLong')
        self.short_sign = data.pop('signMessage')
        self.next_location_id = data.pop('nextLocID')
        self.next_stop_seq = data.pop('nextStopSeq')
        self.last_location_id = data.pop('lastLocID')
        self.last_stop_seq = data.pop('lastStopSeq')
        self.garage = data.pop('garage')
        self.extra_trip_id = data.pop('extraTripID')
        self.extra_block_id = data.pop('extrablockID')
        # Not currently implemented by Trimet as of January 19, 2014
        self.vehicle_load = data.pop('vehicleLoad', None)
        self.off_route = data.pop('offRoute', None)
        self.in_congestion = data.pop('inCongestion', None)
        assert len(data) == 0, "Data from query remains"
