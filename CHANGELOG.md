# Changelog

One entry per commit, newest first. Entries are keyed by commit subject.

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
