# What the Prisma adapter needs (the physics)

Every item is tagged with where it comes from:
- **ask** — must come from the user (contract)
- **derive** — compiler computes it from other inputs (IR)
- **fixed** — adapter constant, no input needed

## A. `schema.prisma`

### Datasource / generator block — all **fixed**
```
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }
generator client { provider = "prisma-client-js" }
```
Adapter config, not contract. (Provider could be an adapter option later; still
never in the contract.)

### Per model
| Prisma needs | Source | Notes |
|---|---|---|
| model name | **ask** | entity name |
| table name (`@@map`) | **derive** | naming convention from entity name |

### Per field
| Prisma needs | Source | Notes |
|---|---|---|
| field name | **ask** (MVP) | attribute name. Parking lot: derive from access patterns |
| scalar type (`Int`, `String`, `Boolean`, `DateTime`, `Float`, `BigInt`, `Decimal`, `Json`, `Bytes`) | **derive** | from an abstract *kind* in the contract (`identifier`, `text`, `integer`, `timestamp`, `boolean`, …). The kind→Prisma-type table is adapter-owned |
| optional (`?`) | **ask** | is this attribute allowed to be absent? That's a fact about the domain, not the backend |
| list (`[]`) | **derive** | only appears on relation fields; comes from relation cardinality |
| `@id` | **derive** | the attribute of kind `identifier`; if none, adapter synthesizes one |
| `@default(...)` | **derive** | `autoincrement()`/`uuid()` on synthesized ids, `now()` on a timestamp the user marks as creation time — MVP: only ids |
| `@unique` | **derive** | any attribute an access pattern looks up by with cardinality *one* must be unique. (Also **ask**-able as a domain fact, e.g. email — keep as optional additive input) |
| `@@index([...])` | **derive** | from access-pattern filter/sort fields. Post-MVP |
| `@map` column name | **derive** | naming convention |

### Relations (the part that must be derived, not declared)
Prisma needs, for every relation:
| Prisma needs | Source |
|---|---|
| which two models | **derive** from an access pattern that *navigates* from one entity to another, or an attribute that *references* another entity's identifier |
| cardinality (1:1, 1:n, m:n) | **derive** — the "one/many" declared on the navigating access pattern's output, or the fact that a reference attribute lives on the "many" side |
| the FK scalar field + `@relation(fields:[…], references:[…])` on the owning side | **derive** — always the "many" side; name by convention (`userId`) |
| the back-relation field on the other side (Prisma requires both sides) | **derive** — Prisma quirk; the contract must never know it |
| `onDelete` behaviour | **fixed** default for MVP (Prisma default) |
| m:n join table | **derive** — implicit `@relation` if neither side needs extra data |

**Consequence for the contract:** the only thing the user states is that an
attribute *references* another entity (`"references": "User"`), or that an
access pattern walks from one entity to another. Everything in this table falls
out of that.

## B. Generated query functions (one per access pattern)

| Prisma needs | Source | Notes |
|---|---|---|
| function name | **ask** | access-pattern name |
| parameters + TS types | **ask** | pattern `input` (name + kind); kind→TS type is adapter-owned |
| return type | **derive** | from output shape + cardinality |
| which model to start from | **derive** | the entity the output shape is anchored on |
| method: `findUnique` / `findFirst` / `findMany` / `groupBy` / `aggregate` / `count` | **derive** | `findUnique` iff filter is by a unique field and cardinality one; `groupBy` iff output has per-group aggregates; `count` iff output is a single scalar count; else `findMany` |
| `where` clause | **derive** | from the pattern's filter conditions, with inputs bound as parameters |
| `select` / `include` | **derive** | `select` from output shape; `include` when shape crosses a relation |
| `by` + `_count/_sum/_avg/_min/_max` | **derive** | from output shape: which fields are plain per-group keys vs aggregates |
| `having` | **derive** | any filter condition on an aggregated value |
| `orderBy` | **ask** | ordering is a genuine requirement of the pattern ("top offenders first"), not derivable |
| `take` / `skip` | **ask** (optional) | limit is a genuine requirement when present |
| distinct | **derive** | if output shape asks for unique values of a non-key field |

## What this tells us about the contract

Everything in the **ask** column, deduped:

- entity name
- attribute name, kind, optional?  (MVP; attributes may later be derived)
- attribute *references* another entity  (the *only* relation input)
- per access pattern: name, inputs (name+kind), output shape (which entity /
  which fields / per-group vs aggregate), cardinality (one/many/scalar),
  filter conditions in an abstract predicate vocabulary, ordering, optional limit

Nothing in that list mentions Prisma, keys, indices, relations tables, methods.
Everything else Prisma needs is in the **derive** column. That is the boundary.

The open question (next step) is only the *shape* of "output shape + filter
conditions" — how a user says "one row per src_ip with a count of failed logins
since T, more than N" without naming group_by/having.
