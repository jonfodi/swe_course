## data structure learning + real system building 

# building a cyber data processing system 
thinking of questions cyber people wanna know and the resulting access patterns 
then the ds + a that make these efficient 
goal is for each question to motivate a new ds + a 
- but also want to demonstrate the same ds used for different a depending on what data we need 

# lenses im using to solve/optimize these problems 
what ds do we need to solve this?
- totally feasible to use multiple like in q1. building a intermediate structure to make the problem easier 
- also super useful to create ds at write time that will save query time 
    - like in q2 when creating the hash map avoids the need to loop through the whole list 
## useful stuff 
# bisection
used for filtering lists 

bisect_left(a, x) = first index where a[i] >= x --> cutoff included
bisect_right(a, x) = first index where a[i] > x --> cutoff excluded

return len(a) - bisect(a, cutoff)

use key if your list is a tuple and you need to sort by a specific item in the tuple
bisect_left(conns, cutoff, key=lambda c: c[0]) -> c[0] = first element of the tuple

# ultimate goals 
- decompose real world app questions into ds + a problems 
- learn the uses of the common data strucutres 
    - HM, graph, stack, queue, heap, LL? 
- map algorithms to app level data access questions 
- build a generic data fetcher (DB)
    - everything well have built will be bespoke for the cyber application. optimized for the exact query but hard to maintain 
    - use this motivation to build a generic fetcher that loses the perofrmance but greatly simplifies the maintenance 


# type safety across the api boundary
the frontend needs to know the shape of what it's fetching. the question is who
owns that shape and how the two sides stay in agreement.

## the problem
cyber.py stores logs as bare tuples. returning those directly gave us:

    [["2024-01-01T08:41:00", "10.0.0.5", "alice", true], ...]

positional. the frontend has to write log[3] and *know* index 3 is success.
that convention lived in a single comment in cyber.py -- nothing enforced it,
nothing exported it, the frontend couldn't see it. reorder the tuple and the
table renders wrong silently.

## what we're doing now
three layers:

1. **internal** (cyber.py) -- AuthLog is a NamedTuple. still a tuple, so it's
   sortable and works with bisect, but `log.success` replaces `log[3]`. raw
   tuples get normalised into AuthLog at ingest.
2. **the contract** (schemas.py) -- AuthLogOut, a pydantic model, declared on
   the route via `response_model=`. this is what goes over the wire:

       [{"timestamp": "...", "src_ip": "...", "username": "...", "success": true}]

   self-describing. no conventions to remember.
3. **frontend** -- reads those field names directly.

kept separate on purpose: how we *store* data and what we *send* should be free
to diverge, so an internal refactor isn't a breaking api change.

a nice side effect of response_model: the shape now appears in /openapi.json and
in the live docs at /docs. accurate by construction, because it's the same
declaration that does the serialising.

conventions settled: snake_case on the wire (matches the backend, one less
transform), bare array rather than an envelope, naive datetimes.

## the options, minimal to maximal
| | drift caught | cost |
|---|---|---|
| **1. nothing** — plain jsx, no types | never. `undefined` shows up in a table cell | zero |
| **2. jsdoc typedef** — `/** @typedef {{...}} AuthLog */` | typos + wrong field names, in-editor | zero, no build change |
| **3. hand-written TS types** | frontend-internal mistakes only | convert to .tsx |
| **4. zod at the fetch boundary** | **yes, at runtime, loudly** | one extra dep, schema written twice |
| **5. codegen from openapi.json** | impossible by construction | generated files + regen step |
| **6. TS backend, shared schema module** | impossible by construction | monorepo, and you give up python |

**we are at 1**, heading toward 2 or 4.

why not the others:

- **3 is weaker than it looks.** TS types are erased at runtime. `await
  res.json()` returns `any`, so `as AuthLog[]` is a promise you made up, not a
  check. it makes the frontend consistent with its *assumption* about the
  backend without ever verifying the assumption.
- **4 (zod) is the real fix** and works fine against a python backend -- zod
  validates the json after it arrives, it doesn't care what produced it.
  pydantic validates on the way out, zod on the way in, neither knows the other
  exists. still two declarations, but drift becomes a loud error naming the bad
  field instead of silent undefined. also the right place to do
  `z.coerce.date()` so components get real Date objects.
- **5** is what shops with separate frontend/backend teams use. for three
  endpoints we own both sides of, the regen step costs more than the mistakes
  it prevents.
- **6** is genuinely the cleanest -- one schema file imported by both sides,
  rename a field and both fail to compile at once. needs real code sharing
  though (a monorepo; two TS repos with copy-pasted types have the same drift
  problem). not worth rewriting cyber.py in TS when the python data structures
  are the point of this project.

the tax we're accepting: one shape declared twice. deliberate, not accidental.

# todo 
- different algos on the HM 
- new DS 
    - graph, stack? queue? idek 
- ConnectionLog is still a bare tuple (conn_log[1], conn_log[2] in cyber.py) --
  same NamedTuple treatment when we build that endpoint
- tests/test_main.py is stale: imports failed_attempts_in_window and
  malicious_ip_connections as module-level funcs, they're Cyber methods now
