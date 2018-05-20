import bisect
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import logging
import threading
from typing import Tuple

logger = logging.getLogger(__name__)


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kw):
        self._paths = kw.pop('__paths')
        logger.debug('Paths %s', self._paths)
        super(BaseHTTPRequestHandler, self).__init__(*args, **kw)

    def log_message(self, fmt, *args):
        logger.info(fmt, *args)

    def do_GET(self):
        self.protocol_version = 'HTTP/1.1'
        try:
            for path, method in self._paths:
                if self.path.startswith(path):
                    # if it's longer then it must have a / at the end
                    if (len(self.path) > len(path) and
                            self.path[len(path)] != '/'):
                        continue
                    logging.debug('Matched %s with %s', path, self.path)
                    status, message = method(self.path[len(path):] or None)
                    break
            else:
                status, message = HTTPStatus.NOT_FOUND, None
            logging.debug('Status %s with %s', status, message)
        except:
            status, message = HTTPStatus.INTERNAL_SERVER_ERROR, None
            logger.exception('Failed serving %s', self.path)

        if message and not isinstance(message, bytes):
            message = message.encode('utf-8')
        self.send_response(status)
        if message:
            self.send_header('Content-Length', len(message))
        else:
            self.send_header('Content-Length', 0)

        self.end_headers()
        if message:
            self.wfile.write(message)


class Server:
    """Simple HTTP server

    Parameters
    ----------
    server_address
        A tuple containg the address and the port number to bind to
    ssl_cert
        Path to a certificate file to use the HTTPS protocol
    """
    def __init__(self, server_address: Tuple[str, int], ssl_cert: str=None):
        self._thread = None
        self._paths = []
        self._thread = None
        logger.info('Serve on %s', server_address)

        self._httpd = HTTPServer(server_address, self._make_handler)
        if ssl_cert:
            logging.debug('Enable SSL: %s', ssl_cert)
            import ssl
            self._httpd.socket = ssl.wrap_socket(
                self._httpd.socket,
                certfile=ssl_cert,
                server_side=True,
            )


    def _make_handler(self, *args, **kwargs):
        return Handler(*args, **kwargs, __paths=self._paths)

    @property
    def is_running(self):
        """Returns true if the HTTP routes are being served."""
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        """Start a thread to serve the routes.

        Can only be called once.
        """
        self._thread = threading.Thread(target=self._serve)
        self._thread.start()

    def _serve(self):
        logger.info('Start server')
        self._httpd.serve_forever()

    def stop(self):
        """Stops the service waiting for any running query.

        After calling this method the object must not be used anymore.
        """
        logger.info('Stop server')
        if self._thread:
            self._httpd.shutdown()
            self._thread.join()
        self._httpd.server_close()

    @property
    def address(self):
        return self._httpd.server_address

    def join(self):
        """Wait forever.
        """
        if self._thread:
            self._thread.join()

    def route(self, path: str):
        """Register a new route

        Parameters
        ---------
        path
            The base route to register the function call for it can be
            called also while the service is running.
            The path parameter will contain anything after the path, including trailing /
        """
        def register(method):
            bisect.insort(self._paths, (path, method))
            return method
        return register
