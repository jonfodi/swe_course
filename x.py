
cache = {}
nex = {}
before = {} 
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
    return result

def handle_duplicate_entries():
    global oldest, newest, before
    # this is the node after the input. 
    next = nex[inp] 
    # this is the node before the input 
    prev = before[inp]
    
    # guards against None (for when input is the oldest / or newest)
    if prev is not None: 
        # the previous node had next = input. now its next is input's next. 
        nex[prev] = next
    else: 
        # input was the oldest therefore before[input] = None. set its next to now be None
        before[next] = None
    if next is not None:
        # the next node had before = input. now its before is input's before.
        before[next] = prev
    
    if inp == oldest:
        oldest = next

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

def update_cache(inp, result, cached):
    global oldest, newest, before
    # write result of inp to cache {inp: result}
    if not cached:
        print('not cached')
        cache[(inp)] = result 

    # duplicate inputs. move the input to the newest and update the ordering   
    # more readable logic for this? maybe inp in cache? cause whats diff between using nex and before   
    if inp in nex:
        handle_duplicate_entries()

    # log inp to ordering dict {inp: next_input}
    nex[(inp)] = None  # latest inp (no next yet)
   
    # first pass guards / logic  
    if not oldest:
        oldest = inp 
    if not newest:
        newest = inp
        return # weird control flow but safe to return cause this is only happening on the first input

    # newest is the previous input until we update it. 
    # set the previous inputs next to be the current input 
    nex[newest] = inp
    # set the current inputs before to be the previous input 
    before[inp] = newest
    # update newest 
    newest = inp 

    if len(cache) > max_in:
        evict_lru()

    return
    



add(1,1)
add(1,2)
add(1,3)
add(1,1)
print(oldest) # (1,2)
print(cache) # { (1,1): 2, (1,2): 3, (1,3): 4}
print(nex) # { (1,1): None, (1,2): (1,3), (1,3): (1,1)}
print(before) # { (1,1): (1,3), (1,3): (1,2): (1,2): None }
print(oldest) # (1,2)
print(newest) # 
# print(oldest) # (1,2)
# print(newest) # (1,4)
