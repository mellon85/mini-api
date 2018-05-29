import unittest
from http.client import HTTPConnection

import mini_api

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.conn = None
        self.server = mini_api.Server(server_address=('localhost', 0))

    def tearDown(self):
        self.server.stop()
        if self.conn:
            self.conn.close()

    def test_stop_without_start(self):
        """ Stop the service without starting it """
        self.assertFalse(self.server.is_running)
        self.server.join()
        self.assertFalse(self.server.is_running)
        self.server.stop()
        self.assertFalse(self.server.is_running)
        self.server.join()
        self.assertFalse(self.server.is_running)

    def test_no_routes(self):
        """ Start and stop the service """
        self.assertFalse(self.server.is_running)
        self.server.start()
        self.assertTrue(self.server.is_running)
        self.server.stop()
        self.assertFalse(self.server.is_running)
        self.server.join()
        self.assertFalse(self.server.is_running)

    def test_single_route(self):
        @self.server.route('aaa')
        def route(args):
            self.assertEqual(args, None)
            return 202, 'aa'

        self.server.start()
        for verb in ('GET', 'HEAD'):
            with self.subTest(verb=verb):
                self.conn = HTTPConnection('localhost', self.server.address[1])
                self.conn.request(verb, 'aaa')
                response = self.conn.getresponse()
                self.assertEqual(response.status, 202)
                if verb == 'GET':
                    self.assertEqual(response.readlines(), [b'aa'])
                self.conn.close()

    def test_single_route_params(self):
        @self.server.route('aaa')
        def route(args):
            return 200, args

        self.server.start()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaa/bbb')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.readlines(), [b'/bbb'])

    def test_single_route_params_trailing(self):
        @self.server.route('aaa')
        def route(args):
            return 200, args

        self.server.start()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaa/')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.readlines(), [b'/'])

    def test_single_route_params_deep(self):
        @self.server.route('aaa')
        def route(args):
            return 200, args

        self.server.start()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaa/bbb/ccc')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.readlines(), [b'/bbb/ccc'])

    def test_overlapping_routes(self):
        """ 2 Overlapping rules should be choosen correctly"""
        @self.server.route('aaa')
        def route(args):
            self.assertEqual(args, None)
            return 202, 'aa'

        @self.server.route('aaaa')
        def route(args):
            self.assertEqual(args, None)
            return 203, 'bb'

        self.server.start()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaaa')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 203)
        self.assertEqual(response.readlines(), [b'bb'])

        self.conn.close()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaa')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 202)
        self.assertEqual(response.readlines(), [b'aa'])

    def test_overlapping_routes_inverted(self):
        """ 2 Overlapping rules should be choosen correctly"""
        @self.server.route('aaaa')
        def route(args):
            self.assertEqual(args, None)
            return 203, 'bb'

        @self.server.route('aaa')
        def route(args):
            self.assertEqual(args, None)
            return 202, 'aa'

        self.server.start()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaaa')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 203)
        self.assertEqual(response.readlines(), [b'bb'])

        self.conn.close()
        self.conn = HTTPConnection('localhost', self.server.address[1])
        self.conn.request('GET', 'aaa')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 202)
        self.assertEqual(response.readlines(), [b'aa'])

    def test_exception(self):
        @self.server.route('aaa')
        def route(args):
            raise Exception('error')

        self.server.start()

        for verb in ('GET', 'HEAD'):
            with self.subTest(verb=verb):
                self.conn = HTTPConnection('localhost', self.server.address[1])
                self.conn.request(verb, 'aaa/bbb/ccc')
                response = self.conn.getresponse()
                self.assertEqual(response.status, 500)
                self.assertEqual(response.readlines(), [])
                self.conn.close()

    def test_utf_data(self):
        @self.server.route('aaa')
        def route(args):
            return 300, "ÂÂ"

        self.server.start()

        for verb in ('GET', 'HEAD'):
            with self.subTest(verb=verb):
                self.conn = HTTPConnection('localhost', self.server.address[1])
                self.conn.request(verb, 'aaa/bbb/ccc')
                response = self.conn.getresponse()
                self.assertEqual(response.status, 300)
                if verb == 'GET':
                    self.assertEqual(response.readlines(),
                                     [b'\xc3\x82\xc2\x89\xc3\x82'])
                self.conn.close()

    def test_404(self):
        """ Query non existing route """
        self.server.start()

        for verb in ('GET', 'HEAD'):
            with self.subTest(verb=verb):
                self.conn = HTTPConnection('localhost', self.server.address[1])
                self.conn.request(verb, 'aaa/bbb/ccc')
                response = self.conn.getresponse()
                self.assertEqual(response.status, 404)
                self.assertEqual(response.readlines(), [])
                self.conn.close()
