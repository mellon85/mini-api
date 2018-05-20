# mini-api

Python minimalistic HTTP(S) server

Some small long running utilities don't need fancy webframeworks to offer
simple APIs over HTTP without any additional dependency that this module.

It spawns a thread to process incoming requests.

```python
import mini_api

server = mini_api.Server(server_address=('localhost', 8888))

@server.route('aaa')
def route(args):
    return 200, 'All good'

server.start()

...

server.stop()
```
