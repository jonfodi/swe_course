# Changelog

One entry per commit, newest first. Entries are keyed by commit subject.

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
