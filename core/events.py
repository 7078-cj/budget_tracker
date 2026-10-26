"""Tiny pub/sub so modules stay decoupled: data layer emits, views subscribe."""
_subscribers = []

def subscribe(fn):
    _subscribers.append(fn)

def emit():
    for fn in _subscribers:
        fn()
