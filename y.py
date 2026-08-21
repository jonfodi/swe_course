cache = {'x': 3}
res = 1 + 2
c = cache.get('x')

if c:
    print('hit')
else:
    print('miss')