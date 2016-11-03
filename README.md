# tornado-sockjs-ext
让你的tornado-sockjs很pythonic


```
class BroadcastConnection(BaseSockJSConnection):
        @event
        def open(self, info):
            print info.path
            print info.path.split("/", 3)[1]

            print self._events

        @event
        def hello(self, msg):
            self.emit("hello", "kokokok")
            print msg
            return msg


BroadcastRouter = SockJSRouter(BroadcastConnection, '/broadcast')
```