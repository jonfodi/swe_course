from structure import Cache

cache = Cache(capacity=3, nodes={}, ends=None)
computed = []


def add(x, y):
    def compute():
        computed.append((x, y))
        return x + y

    return cache.get_or_compute((x, y), compute)


def show(call, result):
    print(f"{call:<18} -> {result}   order={cache.order_oldest_first()}")


for args in [(1, 1), (1, 2), (1, 3), (1, 1), (1, 4)]:
    show(f"add{args}", add(*args))

print()
print(f"5 calls, {len(computed)} computes: {computed}")
