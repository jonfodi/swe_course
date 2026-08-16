# d = {
#     (1,2): "hi"
# }

# print(d[(1,2)])


z = { "op_key" : ({"input1": "result1", "input2": "result2"}, ['input1', 'input2'], 3) } 

# op_cache, lru, cache_size = z["op_key"]
# print(op_cache)
# print(lru)
# print(cache_size)

l = [1,2,"hi"]
if "hi" in l:
    l.remove('hi')

li = [1,2,3]
for result in li:
    print(result)
    if result == 2:
        li.remove(result)

print(li)

# li.remove(1)
# print(li)

# s = set()
# s.add(1)
# s.add(2)
# s.add(1)
# print(s)

