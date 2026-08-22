from structure import Cache

cache = Cache(capacity=3, nodes={}, ends=None)


def add(x, y):
    return cache.get_or_compute((x, y), lambda: x + y)


print(add(1, 1))
print(add(1, 2))
print(add(1, 3))
print(add(1, 1))
