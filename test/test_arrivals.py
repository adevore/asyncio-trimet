import unittest, unittest.mock


import aiohttp
from aiohttp.server import ServerHttpProtocol
import asyncio
import json
import functools
import os
from urllib.parse import parse_qs, urlparse

HOST = "localhost"
PORT = 8080


def find_test_file(me, path):
    return os.path.join(os.path.dirname(me), path)


class AsyncTestCase(unittest.TestCase):
    @staticmethod
    def async_test(func):
        @functools.wraps(func)
        def f(self):
            self.loop.run_until_complete(func(self))
        return f

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.server = self.loop.create_server(TestHTTPServer, HOST, PORT)

    def tearDown(self):
        self.loop.close()

    def assertGetItem(self, collection, key, value, msg=None):
        self.assertIn(key, collection, msg=msg)
        self.assertEqual(collection[key], value)


class TestJSONServer(ServerHttpProtocol):
    def __init__(self, data=None):
        self._data = json.dumps(data).encode('utf8')
        self.type = type

    @property
    def raw_data(self):
        return self._data

    @property
    def json(self):
        return json.loads(self._data.decode('utf8'))

    @json.setter
    def json(self, value):
        self._data = json.dumps(value).encode('utf8')

    def load_file(self, file_name):
        with open(file_name, "rb") as f:
            self._data = f.read()

    def handle_request(self, message, payload):
        assert data is not None
        params = urllib.parse.urlparse(message.path).params
        self.last_vars = urllib.parse.parse_qs(params)
        response = aiohttp.Response(self.transport, 200, close=True)
        response.add_headers(
            ('Content-Type', "application/json"),
            ('Content-Length', len(self.data)))
        response.send_headers()
        response.write(self.data)
        response.write_eof()


class ArrivalTest(AsyncTestCase):
    @AsyncTestCase.async_test
    @asyncio.coroutine
    def test_basic(self):
        self.server.load_file(resolve_test_file("arrivals.json"))
        query = yield from fetch_arrivals(APP_ID, 1234)
        self.assertDictEquals(self.server.last_vars, {
            "appId": APP_ID,
            "json": "true",
            "locIDs", "1234",
            "streetcar": "false"})

        query.query_time.strftime("") == ""

        arrival = query.arrivals[0]
        self.assertEqual(arrival.block, )
        self.assertEqual(arrival.trip, )
        self.assertEqual(arrival.position, )
        self.assertEqual(arrival.departed, )
        self.assertEqual(arrival.detour, )
        self.assertEqual(arrival.direction, )
        self.assertEqual(arrival.estimated, )
        self.assertEqual(arrival.full_sign, )
        self.assertEqual(arrival.location_id, "1234")
        self.assertEqual(arrival.piece, )
        self.assertEqual(arrival.route, )
        self.assertEqual(arrival.scheduled, )
        self.assertEqual(arrival.short_sign, )
        self.assertEqual(arrival.status, )
        



    @AsyncTestCase.async_test
    @asyncio.coroutine
    def test_error(self):
        self.server.load_file(resolve_test_file("arrivals_error.json"))
        with self.assertRaises(aiotrimet.QueryError):
            yield from fetch_arrivals(APP_ID, 1234)
