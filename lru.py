import time
from collections import defaultdict
# [ (count, (x, y)) ]  
class Cache:
    def __init__(self, fn, capacity=2):
        self.fn = fn
        self.results_dict = defaultdict(int) # { (x,y) : (result, results_list_position) }
        self.results_list = [] # [ (x, y) ] 
        self.capacity = capacity 

    def run(self, *args):
        start_time = time.time()
        results = self._run(*args)
        end_time = time.time()
        print(f"Execution took {round(end_time-start_time)} seconds for args {args} and result {results}")
        return results

    def _run(self, *args):
      if args in self.results_dict.keys():
        self.results_list.append(args)
        return self.results_dict[args]
      
      else:
        result = self.fn(*args)
        self.results_dict[args] = result
        self.results_list.append(args)
        if len(self.results_list) > self.capacity:
          result_to_delete = self.results_list[0]
          del self.results_dict[result_to_delete]
          del self.results_list[0]
        return result


def add(x, y):
    time.sleep(1)
    return x + y

def sub(x, y):
    time.sleep(1)
    return x - y


cached_fn = Cache(add)

cached_sub = Cache(sub)

cached_fn = Cache(add, capacity=2)

cached_fn.run(1, 1)
print("should take 1 second")  # stores item, cache: [(1,1)]
print("-------------------------------")
cached_fn.run(2, 2)
print("should take 1 second")  # stores item, cache: [(1,1), (2,2)]
print("-------------------------------")
cached_fn.run(1, 1)
print("should take 0 seconds")  # cache hit, (1,1) moves to most recent: [(2,2), (1,1)]
print("-------------------------------")
cached_fn.run(3, 3)
print("should take 1 second")  # LRU evicts (2,2), cache: [(1,1), (3,3)]
print("-------------------------------")
cached_fn.run(2, 2)
print("should take 1 second")  # cache miss! (2,2) was evicted, stores: [(3,3), (2,2)]