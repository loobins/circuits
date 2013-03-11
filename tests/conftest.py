# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import pytest

import sys
import threading
import collections
from time import sleep
from collections import deque

from circuits.core.manager import TIMEOUT
from circuits import handler, BaseComponent, Debugger, Manager


class Watcher(BaseComponent):

    def init(self):
        self._lock = threading.Lock()
        self.events = deque()

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        with self._lock:
            self.events.append(event)

    def wait(self, name, channel=None, timeout=3.0):
        for i in range(int(timeout / TIMEOUT)):
            if channel is None:
                with self._lock:
                    for event in self.events:
                        if event.name == name:
                            return True
            else:
                with self._lock:
                    for event in self.events:
                        if event.name == name and channel in event.channels:
                            return True
            sleep(TIMEOUT)


class Flag(object):
    status = False


def call_event_from_name(manager, event, event_name, *channels):
    fired = False
    value = None
    for r in manager.waitEvent(event_name):
        if not fired:
            fired = True
            value = manager.fire(event, *channels)
        sleep(0.1)
    return value


def call_event(manager, event, *channels):
    return call_event_from_name(manager, event, event.name, *channels)


class WaitEvent(object):

    def __init__(self, manager, name, channel=None, timeout=3.0):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, *args, **kwargs):
            flag.status = True

        self.handler = self.manager.addHandler(on_event)
        self.flag = flag

    def wait(self):
        try:
            for i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


def wait_for(obj, attr, value=True, timeout=3.0):
    from circuits.core.manager import TIMEOUT
    for i in range(int(timeout / TIMEOUT)):
        if isinstance(value, collections.Callable):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)


@pytest.fixture(scope="session")
def manager(request):
    manager = Manager()

    def finalizer():
        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, "started")
    manager.start()
    assert waiter.wait()

    if request.config.option.verbose:
        Debugger().register(manager)

    return manager


@pytest.fixture(scope="session")
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer():
        watcher.unregister()

    request.addfinalizer(finalizer)

    return watcher


def pytest_namespace():
    return dict((
        ("WaitEvent", WaitEvent),
        ("wait_for", wait_for),
        ("call_event", call_event),
        ("PLATFORM", sys.platform),
        ("PYVER", sys.version_info[:3]),
        ("call_event_from_name", call_event_from_name),
    ))
