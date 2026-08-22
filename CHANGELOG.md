# Changelog

One entry per commit, newest first. Entries are keyed by commit subject.

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
