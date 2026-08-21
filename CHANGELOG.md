# Changelog

One entry per commit, newest first. Entries are keyed by commit subject.

## docs: correctness note for the cache rewrite
2026-08-21

Adds `from-guards-to-guarantees.md`: the seven properties this cache depends
on, seven ways to enforce a property, and the step plan for the rewrite.

**Why:** every branch in the cache exists to keep something true that is
written down nowhere and checked by nothing. Listing the properties first
makes it possible to say what each later change actually removes, instead of
asserting that things got better.
