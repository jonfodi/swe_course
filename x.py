# # d = {
# #     (1,2): "hi"
# # }

# # print(d[(1,2)])


# z = { "op_key" : ({"input1": "result1", "input2": "result2"}, ['input1', 'input2'], 3) } 

# # op_cache, lru, cache_size = z["op_key"]
# # print(op_cache)
# # print(lru)
# # print(cache_size)

# l = [1,2,"hi"]
# if "hi" inp l:
#     l.remove('hi')

# li = [1,2,3]
# for result inp li:
#     print(result)
#     if result == 2:
#         li.remove(result)

# print(li)

# li.remove(1)
# print(li)

# s = set()
# s.add(1)
# s.add(2)
# s.add(1)
# print(s)

# cache = {

#     'x': 1, 
#     'y': 2,
#     'z': 3
# }

# nex - {
#     'x': 'y', 
#     'y': 'z',
#     'z': None
# }

# # globally init oldest to survive 
# oldest = None 

# # write to cache 
# def update_lru(inp):
#     if len(nex) == 0:
#         nex[inp] = None   
    
    
# def write_cache(inp, out):
#     update_lru(inp)
#     cache[inp] = out



# def do_some_shit(inp):
#     # check cache for inp by key 
#     # if entry exists, res = output
#     # if doesnt exist, compute the output 
#     # res = output 
#     # update cache 
#         # write to the LRU 
#         # if the size of the LRU is greater than the max, evict the oldest 
#             # assuming we have a tag on the oldest. we'd need to then find the inp that comes after it. 
#             # if we had a inp: next we can look it up. 
#             # but we'd need to write this data inp. so we need to know which inp preceeded this one when the data comes inp.
#             # at that time we only have the current inp and the oldest.
#         # check size of 
    

cache = {}
nex = {}
before = {} 
last_input = None
oldest = None
newest = None 
max_in = 3

def add(x, y): 
    result = 0
    # check for cache hit
    cached = cache.get((x,y))
    if cached:
        result = cached 
    else:
        result = x + y # add logic so hidden inp this add fn. need to wrap up the cache shit

    update_cache((x,y), result, cached)

def update_cache(inp, result, cached):
    global oldest, newest, last_input
    if not cached:
        # write result of inp to cache {inp: result}
        cache[(inp)] = result 
        if len(cache) > max_in:
            evict_lru()
    # log inp to ordering dict {inp: next_input}
    already_exists = nex.get(inp) != None
    nex[(inp)] = None  # latest inp (no next yet)
    if already_exists:
        # update the pointers after duplicate (inputs next becomes its befores next, its before becomes its nexts before)
        next = nex[inp] 
        before = before[inp] 
        nex[before] = next
        before[next] = before
    
    before[inp] = last_input
    last_input = inp

    # first pass guards / logic  
    if not oldest:
        oldest = inp 
    if not newest:
        newest = inp
        return # weird control flow 

    # set the second newest inp inp ordering dict to point to newest inp {inp: None} -> {inp: latest_input}
    nex[newest] = inp
    # now we've made use of 2nd newest, we can update newest inp 
    newest = inp 
    return
    
def evict_lru():
    global oldest
    # get the oldest node
    to_evict = oldest
    # evict it from cache 
    del cache[to_evict]
    # get the next oldest node
    next_oldest = nex[to_evict]
    # delete oldest entry from ordering dict 
    del nex[oldest]
    # update latest oldest now that we've used previous oldest
    oldest = next_oldest


print(before)
print(last_input)
add(1,1)
# print(cache) # {(1, 1): 2, (1, 2): 3, (1, 3): 4 }
# print(nex) # { (1, 1): (1, 2): (1,4), (1, 4): None}
print("=================================================================================")
print(before)
print(last_input)
# print(oldest) # (1,2)
# print(newest) # (1,4)
