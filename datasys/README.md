# datasys

Describe your data and the questions you ask of it. Get back the data layer.

## What this is

Most applications are not "using a database" — they are running a small set of
known access patterns over a known set of entities. Everything else in a data
layer (indices, materialized views, caches, the shape of the queries) is a
*derivation* of those access patterns. Today that derivation lives in the head
of whoever knows the target stack, and is re-expressed by hand for every
backend: Postgres DDL, Prisma models, Django ORM, hand-rolled dicts in memory.

`datasys` moves that derivation into a compiler.

```
  user spec ──▶ IR ──▶ adapter ──▶ artifacts for your stack
             ▲
             │  the boundary: nothing left of here knows any backend exists
```

- **Input (the contract):** what the user actually knows — the entities, how
  they relate, and each access pattern as *input → output shape*. Nothing else.
- **IR:** the backend-agnostic form of that spec. Sole source of truth for every
  adapter.
- **Adapters:** mechanical renderers. One per target stack. They read the IR and
  emit the files a developer would otherwise write by hand.

## Why the boundary is the product

The contract is the whole value. If a user can express something in the spec
that only makes sense for one backend, the abstraction is already broken at the
front door and no adapter can repair it. So the rule for every field in the
contract is:

> Would this field mean the same thing to someone whose backend is a Python
> `dict`?

If it only makes sense once you've assumed a relational engine (`GROUP BY`,
`HAVING`, "plan steps", operator names) it belongs to an adapter, not the
contract. Users describe **what** the output is and how its rows relate to the
entities; the compiler derives **how**.

## Principles

Two kinds. Keep them separate: the first applies to *any* contract → IR →
fan-out system; the second is specific to this one.

### Meta — true of every system shaped like this

- **Derive everything you can.** Every fact the compiler derives instead of asks
  for is one fewer place the user can be wrong and one fewer place two inputs
  can disagree. Derivation is a correctness move first and a convenience second.
  When deciding whether something is an input or a derivation, default to
  derivation and only promote it to input when it genuinely cannot be inferred.
- **The target defines the physics; the input is where the art is.** What a
  backend needs is a fixed fact (Prisma needs models, fields, types, relations,
  constraints). The design work is entirely on the input side: how do we gather
  enough to satisfy every target without letting the input know any target
  exists.
- **Additive only.** Every change to the contract or IR must be backwards
  compatible. Before adding a field, ask: would a future adapter break this?
  Could a future adapter share it? Sharing is the goal every time.
- **Backends inform the contract, not the reverse.** We learn what the IR must
  carry by building adapters. We do not perfect the contract in the abstract.
- **Deterministic core.** No LLM in the compiler. An LLM may later sit *in front*
  of the contract to turn prose into a spec the user validates — never inside.

## Roadmap

1. **Happy path, end to end — Prisma adapter.** For a spec with a couple of
   entities and two access patterns (a point lookup and a grouped aggregate),
   emit:
   - `schema.prisma` — models, fields, relations
   - one typed function per access pattern wrapping a Prisma Client call; its
     signature is the pattern's input, its return type is the pattern's output
2. **Second adapter — raw parameterized SQL (Postgres).** Deliberately the least
   structured target: it forces the compiler to derive grouping/filtering/joins
   itself rather than lean on an ORM. If the IR is enough for raw SQL, it is
   enough for any ORM.
3. Only then: revisit the contract with what the two adapters taught us. Then
   workload metadata (frequency, volume, staleness) → indices, materialized
   views, cache invalidation derived from the access-pattern dependency graph.


