import time
from collections import defaultdict
# [ (count, (x, y)) ] 
# goal: keep the N most recently used items



class Cache:
    def __init__(self, fn):
        self.fn = fn
        self.results_dict = defaultdict(int) # { (x, y) : result, (a, b): result, (c, d): result }
        # we need to check if 
        self.recently_seen = [] # [ (x, y), (a, b), (c, d) 
        # right now what were doing is adding it to the list, then if its > size we evict [0] 
        self.cache_max = 3


    def run(self, *args):
        start_time = time.time()
        results = self._run(*args)
        end_time = time.time()
        return results

    def _run(self, *args):

      # remove any duplicates 
      self.recently_seen = [res for res in self.recently_seen if res != args]

      self.recently_seen.append(args)

      if len(self.recently_seen) > self.cache_max:
        least_recently_seen = self.recently_seen[0]
        del self.results_dict[least_recently_seen]
        del self.recently_seen[0] # appends are in succession, first element = least recently seen 

      if args in self.results_dict.keys():
        return self.results_dict[args]
      
      else:
        result = self.fn(*args)
        self.results_dict[args] = result
        return result

def add(x, y):
    return x + y

cached_fn = Cache(add)

cached_fn.run(1, 1)
# [ (1,1) ] 
# { (1,1): 2 }

cached_fn.run(2, 2)
# [ (1,1), (2,2) ] 

# { (1,1): 2 ,
#   {2,2}: 4, 
# }

cached_fn.run(3, 3)
# [ (2,2), (3,3) ] 

# { (2,2): 2 ,
#   (3,3): 6, 
# }
cached_fn.run(4, 4)