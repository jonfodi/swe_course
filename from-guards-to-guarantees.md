# Guaranteeing Correctness

A working program depends on things being true that are written down nowhere and checked by nothing. They hold because the author kept them in mind while writing each line.

This is about what you can do instead. The worked example throughout is an LRU cache.

---

## The starting position

A standard LRU cache stores five things:

```
values   key -> value
next     key -> the next-newer key
prev     key -> the next-older key
oldest   the least recently used key
newest   the most recently used key
```

For the operations to return correct results, seven things must be true at all times.

| | Must be true | This is a fact about |
|---|---|---|
| **A** | `values`, `next` and `prev` contain the same keys | linked lists |
| **B** | The oldest key has no `prev` entry; the newest has no `next` entry | linked lists |
| **C** | `next[a] == b` if and only if `prev[b] == a` | linked lists |
| **D** | Following `next` from `oldest` reaches every key exactly once and stops at `newest` | linked lists |
| **E** | `oldest` and `newest` are both set, or both unset | linked lists |
| **F** | The number of stored entries never exceeds the capacity | caches |
| **G** | Following `next` produces keys in the order they were last used | caches |

A typical implementation states none of these and verifies none of them. If one breaks, the failure appears later, somewhere else, as a wrong answer or a `KeyError`.

Look at the right-hand column. **Five of the seven are not about caching.** They are requirements that appeared the moment the ordering was stored as a linked list. Store it differently and they do not apply.

---

## Three things get called correctness

**What the cache must do.** Return the stored value on a hit. Report a miss when the key is absent. Never hold more than the capacity. Evict the least recently used key.

Four sentences. They are true regardless of how anything is stored, and nothing in this document changes them.

**Whether the stored bytes mean anything.** A through E, which together say one thing: *the chain is intact.* The links point at real keys, they agree with each other, and following them walks the whole cache once and stops at the end.

**The code.**

The middle one is not correctness. A cache can have a perfectly intact chain — every link mirrored, traversal clean — and evict the wrong key on every insert. Intact chain, wrong answers.

An intact chain is what makes the answers *meaningful*. It does not make them *right*. It is the precondition for asking the question, and it exists only because of a storage decision.

---

## Correct with respect to what

You cannot ask whether an implementation is correct without a second description to compare against. There are two here: what the cache must do, and the five variables in memory.

Connecting them takes two things, and they are not the same kind of thing.

**A description of what the stored bytes mean.** Take `values`. Start at `oldest` and follow `next` to the end. That traversal produces the ordering. This is not code — it is how you say what the storage represents. It becomes code only if we later compare against a second implementation.

**A function that walks the chain and reports whether it is intact.** This is real code, about twenty lines. It starts at `oldest`, follows `next`, checks it visited every key in `values` exactly once, checks it ended at `newest`, and checks each forward link has a backward link pointing back. Returns true or false. This is step 2 of the plan.

Correct then means two things:

```
1.  Every operation returns what the four sentences say it should.

2.  If the chain was intact before an operation, it is intact after.
```

**Requirement 2 is a conditional and proves nothing on its own.** It says what happens *given* an intact chain. To conclude the chain is always intact you need two premises:

```
the empty cache has an intact chain          base case
requirement 2                                step
──────────────────────────────────────────
every state you can reach has an intact chain
```

The induction runs over the number of operations performed. After zero operations the chain is intact. If it is intact after n operations, it is intact after n+1. Therefore always.

This accounts for a branch present in nearly every cache implementation. `if oldest is None: oldest = key` establishes the base case. The rest of the function is the step. Two different obligations, almost always written in one function with nothing marking the boundary.

**The two requirements are also ordered, not parallel.** Requirement 1 cannot be evaluated until requirement 2 holds, because reading the ordering out of a broken chain loops, raises, or returns a partial sequence, and nothing marks the result as garbage. Intact first. Right answers second.

---

## What the compiler checks

A fixed set of properties, defined by the language specification. For most compiled languages: the source parses, every name is declared, and operand types match the operations applied to them.

It does not check that the program computes the intended result. The set does not grow because a program is important.

**Extracting code into a well-named function checks nothing.** A function named `relink_neighbors` can do the opposite of what its name says. No compiler, linter, or test reports the contradiction. The name is a comment attached to a call site.

---

## Seven ways to make a property hold

Named by what performs the check.

**1. Nothing checks it**

The property is in a comment or implied by a name. Violations are found by a human reading the code, or not found. This is where all seven currently sit, along with Java interface contracts and Haskell's laws.

*Cost: none.*

**2. The violating state cannot be built**

No check runs, because there is no way to construct a state that breaks the property.

Count what this does to property A. With N possible keys, each of the three dictionaries holds some subset, so there are 2^N × 2^N × 2^N states you can build. The ones where all three key sets match number 2^N. At ten keys, roughly one buildable state in a million satisfies A.

Now store one dictionary mapping each key to a record holding the value and both links. Buildable states: 2^N. States satisfying A: 2^N. Every state you can build satisfies it.

The reason is that the value and both links occupy one cell, created and deleted in one operation. There is no operation that adds a value without adding its links, because they are no longer separately addressable.

*Cost: no code. Design time before writing the implementation.*

**3. The compiler checks it**

The property is written as a type declaration and the program is rejected before it runs if the declaration is violated.

Type systems in common languages express: this value is present, this value may be absent, every case of this choice is handled, these two values are not interchangeable. They do not express relationships between the contents of two separate structures, which rules out C and D.

*Cost: roughly 10 to 20 percent more source text.*

**4. The program checks itself while running**

The property is written as a function returning true or false, called after each operation. It reports violations on the paths that execute, and nothing about paths that do not.

*Cost: about 20 lines for this cache.*

**5. A generator searches for counterexamples**

Write a second implementation, slower, whose correctness can be confirmed by reading it. Generate random operation sequences, run both, compare results.

Ten thousand sequences with no disagreement does not establish that the two agree on all inputs. It establishes that no disagreement was found.

*Cost: about 40 lines.*

**6. A proof checker verifies it for all inputs**

The property is written in a language whose compiler demands a proof alongside the code and verifies the proof covers every input, including inputs too large to run.

Checking a proof is fast. Producing one is manual. Rice's theorem establishes that no algorithm decides non-trivial semantic properties of arbitrary programs, so this cannot be automated in general.

Deployed examples: CompCert, a C compiler whose optimizer is proved correct, in which a randomized bug-finder that found wrong-code bugs in every other C compiler found none. seL4, an OS kernel, roughly 10,000 lines of C against 200,000 lines of proof. HACL\*, cryptography proved correct and shipping in Firefox.

*Cost: 10 to 20 times the source text of the implementation.*

**7. Someone else already discharged it**

Use a component where the property is already maintained, by code that many programs exercise daily.

Python's `OrderedDict` maintains insertion order internally and exposes `move_to_end` as a single operation. Built on it, an LRU cache is about fifteen lines and maintains none of A through E by hand. They still exist, inside a C implementation. `functools.lru_cache` is one line and you maintain nothing.

*Cost: usually the lowest available. This is the correct choice for shipping code, and the reason the rest of this document is a learning exercise rather than a recommendation.*

---

## The rule underneath step 1

Property A exists because one fact is written in three places.

"Key K is in the cache" is recorded in `values`, in `next`, and in `prev`. Three records of one fact means two of them can be wrong. A is the requirement that they never are.

Write the fact once and A is not enforced, not checked, and not maintained. It has nothing left to be about.

**Generally: any property of the form "these must agree" is removed by making them one thing.** The work is finding a way to hold, in one place, what was held in several.

This is not a language feature. Databases call it normalization and the reasoning is identical: a customer name stored in both the customer table and the order table can disagree, so store it once. The same edit applies in Python, Rust, or anything else.

---

## Engineering tradeoffs

**Invariants trade, they do not vanish.** Dropping the linked list removes C and D. Store an access counter with each entry and evict the minimum, and what arrives instead is: the counter must strictly increase and never repeat, and eviction now scans every entry. Add a heap to avoid the scan and you get the heap's ordering property plus a map from key to heap position that must stay in sync with the entries — which is property A again in different clothes.

Sometimes the replacement set is genuinely smaller. Sometimes it is the same size in a different place. It is worth counting before switching.

**Reach for the representation before the language.** The strongest option on the list — the violating state cannot be built — is not a compiler feature. It is a data layout decision, available in Python exactly as in Rust. Step 1 removes three properties with no language help at all. Change the language when you have collapsed what collapses and something important is still left over.

**The language question has a narrower answer space than it appears.** C and D relate the contents of two structures. No mainstream type system expresses that — not Rust's, not Haskell's. If a property of that shape must be guaranteed, the honest options are a check that runs, a component that already handles it, or a proof assistant. "Which language makes this a compile error" has no mainstream answer.

**The abstract description is not a destination.** The four sentences describing what the cache must do are fixed. They are true before step 1 and after step 5. What moves is the distance to them, and it closes from both ends: the four sentences get stated more precisely, and storage that carries no meaning gets removed. `next`, `prev`, `oldest` and `newest` are bookkeeping for a linked list, not parts of a cache. Each one that goes takes its maintenance requirement with it.

---

## Plan

Each step produces a working cache. Rows get filled in as steps are completed.

| Step | Stored | Maintained by hand | Enforced, and by what |
|---|---|---|---|
| Now | 3 dictionaries, 2 end variables | A B C D E F G | nothing |
| 1 | 1 dictionary of records, 1 ends value | C D F G | A B E — cannot be built |
| 2 | same | G | C D F — a function that runs |
| 3 | same, annotated | G | plus shape errors — the compiler |
| 4 | Rust: nodes in one collection, links as positions | G | C D bounded to one module |
| 5 | not scheduled | — | — |

**1. Store each fact once.** One dictionary of records, one value holding both ends. A, B and E stop existing, and the branches testing for them have no reachable case and get deleted.

**2. Write the chain check.** Twenty lines that walk the chain and report whether it is intact, called after every operation. A violation gets reported at the operation that caused it instead of surfacing later somewhere unrelated.

**3. Add type annotations and run a checker.** Find the exact boundary of what a type system catches, by watching it catch shape errors and stay silent on C and D.

**4. Rewrite in Rust.** A doubly linked list needs two modifiable references to each node and the borrow checker rejects that, so the current design does not compile. Find out what layout it forces instead.

**5. Proof.** Not scheduled. Listed so the range is visible.

---

**References**

- C.A.R. Hoare, "Proof of Correctness of Data Representations" (1972). Nine pages. The description of what stored bytes mean, and the intactness check, are its subject — named there abstraction function and representation invariant.
- MIT 6.031, *Software Construction*. Public course materials, both with worked examples.
