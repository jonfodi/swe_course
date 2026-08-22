# Changelog

One entry per commit, newest first. Entries are keyed by commit subject.

## remove the dead guard in the eviction loop
2026-08-22

Drops `and self.ends is not None` from the eviction loop condition.

**Why:** it can never be false when the loop runs. Eviction is only called at
the end of the miss path, right after the new node is appended, so every key in
the dictionary is linked and a non-empty dictionary guarantees the ends marker
is set. It never fired across 25,000 operations.

Its only possible effect arrives when the invariant is already broken, and then
it is harmful: the loop exits quietly and leaves the cache permanently over
capacity with nothing reporting it. Without the guard the next line raises
`AttributeError` at the operation that caused it. Verified both — behaviour
unchanged across 25,000 further ops at five capacities, and a deliberately
corrupted state now raises instead of returning silently.

A guard against a state the invariant forbids does not prevent a failure. It
converts a loud one into a silent one.

## record what step 1 taught
2026-08-22

Four additions to `from-guards-to-guarantees.md`, all from doing the work
rather than planning it.

**Where the check can run.** The chain is broken partway through every
operation, on purpose: unlinking leaves it broken on exit, appending finds it
broken on entry, and only the whole operation holds at both ends. So the check
belongs after complete operations and would report failures on correct code if
placed inside them. Includes the distinction that "the ends marker is unset"
means the chain is empty, not the cache — true at boundaries, false in between.

**A new section on the same question at a function boundary.** The doc only
covered enforcement inside a data structure. Returning a value that has to
signal both "absent" and "the stored value" is the identical problem one level
out, with a third party silently constrained and a failure mode that degrades
instead of breaking.

**Two tradeoffs.** A guard against a state the invariant forbids converts a
loud failure into a silent one. And not re-deriving what the caller already
knows, which decided two designs after the original collapse.

**The plan is now partly fact.** Step 1 is marked done with what it actually
produced, including the unpredicted one: non-optional end fields forced the
chain-became-empty case into the open, and a defensive guard got written anyway
despite the principle being known.

## expose the recency order
2026-08-22

`Cache.order_oldest_first` walks the chain and returns the keys from oldest to
newest. `x.py` prints it after each call and counts how many times the compute
function actually ran.

**Why:** the ordering is observable — it decides which key eviction takes — so
reporting it is part of the interface, not a leak of the representation.
Exposing `nodes` or `ends` would be the leak; those are storage, and no sequence
of operations can tell how they are arranged.

Compute counting deliberately stays in `x.py`. The caller supplies the compute
function, so it already knows exactly when computation happens. Counters on
`Cache` would record the same fact in a second place, where the two could
disagree — the problem step 1 removed.

The method name carries the direction because "order" alone does not say which
end it starts from and both readings are plausible.

## remove the old cache implementation from x.py
2026-08-22

Deletes `update_cache`, `handle_duplicate_entries`, `evict_lru` and the prints
of the old module-level state. `x.py` is now the cache instance, `add`, and a
few calls.

**Why:** they referenced `nex`, `before`, `oldest`, `newest` and `max_in`, none
of which existed after the state moved into `Cache`, so `x.py` had not run since
that switch. The write path they implemented now lives in `Cache` and is
verified. Preserved at `bc3db76` if the old version is ever wanted.

## name the pre-state in append
2026-08-21

`_append_as_newest` reads the previous newest into a local before overwriting
`ends.newest`.

**Why:** the expression `self.ends.newest` meant the old newest on one line and
the new one two lines later. The name was stable, the referent was not, and the
three lines had to run in exactly that order because the last destroyed what
the first two read — an ordering dependency with nothing marking it. Naming the
pre-state removes both the double meaning and the ordering dependency; the
middle lines can now be reordered freely.

Formal specification languages have dedicated notation for the pre-state
(`old` in Eiffel, primed variables in Z). Python has none, so a local variable
is the substitute.

## wire ordering and eviction into the cache
2026-08-21

`get_or_compute` now maintains the recency chain. Three internal operations:
`_unlink` closes the chain over a node, `_append_as_newest` extends the newest
end, `_evict_until_within_capacity` drops from the oldest end. A hit unlinks
then appends; a miss appends then evicts.

**Why:** a single `touch(key)` covering both branches would have to work out
whether the node is currently linked — which both callers already know. The hit
branch knows it is, the miss branch knows it isn't. Re-deriving that from the
data is the same shape as the problem step 1 removed: asking a question you
already have the answer to, where the two answers can disagree. Neither branch
tests for anything.

`compute()` still runs before anything is written, so a raising compute leaves
the chain untouched rather than half-linked.

Making `Ends` fields non-optional in the previous commit paid off here: when
`_unlink` removes the last node there is no key left to store in `oldest` or
`newest`, so the "chain became empty" case had to be written explicitly instead
of papered over with a null.

**Verified:** chain walked after every operation across 3000 random ops, and
order compared against `OrderedDict` across 3000 more with an exact match.
Covered: hit on oldest, newest and middle; single-node chain; capacity 0; and
`compute()` raising.

**Not done:** `x.py` still holds the old ordering functions and trailing prints
referencing globals that no longer exist, so it does not run.

## move the hit/miss decision inside the cache
2026-08-21

`Cache.get_or_compute` takes a key and a way to compute the value, decides hit
or miss internally, and returns a result. `add` is one line and never receives a
miss signal. The module-level dicts are gone from `x.py`.

**Why:** returning a bare value meant `None` had to mean both "not present" and
"the stored value is None". The caller could not tell them apart, and the
agreement about which it meant lived in two authors' heads and nowhere in the
program. Deciding internally removes the signal rather than disambiguating it —
the check happens on the node, where it was never ambiguous. `None` is now
cacheable and nothing special handles it.

**Not done:** ordering and eviction. Nodes go in with null links and `ends`
stays unset, so this is currently an unbounded memo, not an LRU cache. The old
ordering functions are still in `x.py` and still reference globals that no
longer exist; they are the reference for rebuilding the write path.

## store each fact once
2026-08-21

Adds `structure.py`. One dictionary of `Node` records holding value, prev and
next, replacing three parallel dictionaries. `Ends` replaces the separate
`oldest` and `newest` variables. Nothing imports it yet.

**Why:** three dictionaries meant "key K is in the cache" was recorded in three
places, and any two of them could disagree — that is all property A ever was.
One record per key leaves nothing to disagree, because the value and both links
are created and deleted in a single operation. `Ends` requires both fields, so
"one set, one unset" has no representation. Properties A, B and E stop being
maintained and start being unconstructible.

## docs: correctness note for the cache rewrite
2026-08-21

Adds `from-guards-to-guarantees.md`: the seven properties this cache depends
on, seven ways to enforce a property, and the step plan for the rewrite.

**Why:** every branch in the cache exists to keep something true that is
written down nowhere and checked by nothing. Listing the properties first
makes it possible to say what each later change actually removes, instead of
asserting that things got better.
