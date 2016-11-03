# -*- coding: utf-8 -*-
from inspect import getmembers, ismethod

import gevent
from sockjs.tornado import SockJSConnection
from sockjs.tornado import SockJSRouter


def event(name_or_func):
    if callable(name_or_func):
        name_or_func._event_name = name_or_func.__name__
        return name_or_func

    def handler(f):
        f._event_name = name_or_func
        return f

    return handler


class BaseSockJSConnection(SockJSConnection):
    def on_open(self, request):
        setattr(
            self,
            '_events',
            {e._event_name: e for _, e in getmembers(self, lambda x: ismethod(x) and hasattr(x, '_event_name'))}
        )
        _p = request.path.split("/")
        self.room = _p[1]
        self.name = _p[1] + "_" + _p[2]
        self.token = _p[3]

        gevent.spawn(self._events["open"], request).join()

    def on_message(self, msg):
        name, data = msg.split(',', 1)

        if name in self._events:
            a = gevent.spawn(self._events[name], data)
            a.join()
            r_data = a.value
            if r_data:
                self.emit(name + "_return", r_data)

    def on_close(self):
        gevent.spawn(self._events["close"]).join()

    def emit(self, name, data):
        gevent.spawn(self.send, name + "_return," + data).join()

    @event
    def open(self, msg):
        print msg

    @event
    def close(self):
        pass


if __name__ == '__main__':
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
