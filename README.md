# Modelling Case Study — Drone Insurance Pricing Model

A Python reimplementation of an Excel-based drone insurance rating model
(`Initial File - hx Interview Model.xlsm`), plus two pricing extensions.

## What this model does

Given a fleet of drones (and their detachable cameras), it calculates
insurance premiums for three lines of cover:

- **Hull** — damage to the drone itself: `value × base rate × weight-band adjustment`
- **Third Party Liability (TPL)** — liability if a drone causes injury or
  damage, priced using a Riebesell increased-limit-factor (ILF) curve, the
  standard actuarial way of pricing "how much more to charge for a bigger
  cover limit"
- **Camera** — detachable cameras are priced off the highest hull rate among
  drones that both have a detachable camera and a nonzero value, since a
  camera's flight risk mirrors whichever drone it might be mounted on

Net premiums are grossed up for brokerage (`net / (1 - brokerage)`) to get
what the customer is actually charged.

## Project structure

```
Modelling Case Study/
├── core/                       the calculation engine
│   ├── constants.py            raw parameters (rates, brokerage, weight table)
│   ├── library.py               pure calculation functions, one per Excel formula
│   └── graph.py                 Node/NODES dependency graph + resolve() engine
├── app/                        things that use the engine
│   ├── models.py                 Customer/Drone/Camera dataclasses
│   ├── main.py                   solves the exercise's own data schema
│   └── extensions.py              top-n pricing rules
├── test/
│   └── test.py                    smoke tests for every core.library function
```

`core` never imports from `app` — the engine has no idea what uses it.
`graph.py` is the only file that imports both `constants.py` and
`library.py`; neither of those import each other, avoiding a circular
import while still letting `Node.func` be an actual function reference
(so Ctrl+Click jumps straight to its implementation in `library.py`).

## Running it

All entry points must be run as modules, from the `Modelling Case Study`
folder itself (the parent of `core/`, `app/`, and `test/`):

```
python -m app.main
python -m app.extensions
python -m test.test
```

## How the graph works

`core/library.py` holds one pure function per calculation — `hull_premium`,
`tpl_ilf`, `camera_rate`, and so on — each taking plain values in and
returning a plain value out, with no knowledge of where its inputs came
from or what happens to its output. `core/graph.py` connects them: a
`Node` is a small record saying "to compute X, call this function on
these named inputs" — it holds no value itself, only metadata. `NODES` is
a dictionary of every Node, keyed by name; a Node's `deps` list names the
other Nodes (or raw constants, or per-drone inputs) it needs first.

`resolve(node_id, context)` walks this graph. Given the name of whatever
you want (e.g. `"hull_premium"`), it checks whether that value is already
known — sitting in `context` as a constant or a runtime input — and
returns it immediately if so; otherwise it resolves that Node's `deps`
recursively first, then calls the Node's function with the results,
caching the answer back into `context` so shared dependencies are never
recomputed. This is what makes it possible to ask for one final figure
(e.g. `gross_total`) without manually writing out every step feeding into it.

## Files

**`app/main.py`** solves the exercise as specified, working directly
against the nested dictionary schema from the starter file
(`get_example_data()`) rather than the classes in `models.py`. For each
drone it calls the relevant `core.library` functions in the same order
the Excel model computes them, then does the same for cameras, and
finally populates the `net_prem`/`gross_prem` summary.

**`app/extensions.py`** implements the two top-n pricing rules below, on
top of a `Customer` (from `models.py`) rather than the raw dictionary
schema, since ranking a fleet requires having every drone/camera in scope
at once — unlike `main.py`'s one-drone-at-a-time loop. It reuses the same
`core.library` functions for the underlying math, then layers the ranking
logic on top.

## Extension 1 — top-n drones by premium

> Customers may have a large number of drones but warrant that they will
> only fly a small number (n) at any one time. Charge the full rate for
> the n drones with the highest calculated premiums, and a fixed base
> premium of £150 for the rest.

Every drone's full premium (hull + TPL) is calculated as normal, then
ranked descending. The top `n` (`max_drones_in_air`) keep their real
premium; every drone beyond that is charged the flat £150 instead,
regardless of what its own calculation would have produced.

## Extension 2 — top-n cameras by value

> If there are more cameras than drones, charge the full rate for the n
> cameras with the largest values, and a fixed premium of £50 for the rest.

Only applies when `len(cameras) > len(drones)`. When it does, cameras are
ranked by value descending; the top `n` are priced normally
(`value × shared camera rate`), the rest get the flat £50.

**Key assumption**: a drone flattened to £150 under Extension 1 still
counts toward the camera rate lookup using its *real* hull rate — the
flat rate is a billing decision, not a change to the drone's actual risk
profile.

## Other assumptions made along the way

- **"Calculated premium" for Extension 1's ranking** = hull + TPL combined,
  not either line individually.
- **Extension 2's `n`** reuses the same `max_drones_in_air` as Extension 1
  (not a separate "max cameras in air" figure), since at most `n` drones —
  and therefore at most `n` cameras — can ever be airborne at once.
- **Tie-breaking** at the n/n+1 boundary is whatever Python's stable sort
  produces (original list order preserved among equal premiums) — not a
  deliberately chosen rule.
- **Rounding**: currency-producing functions (`hull_premium`,
  `tpl_premium`, `camera_premium`, the summary sums, `gross_premium`)
  round to 2 d.p. internally; rate/ratio functions (`hull_final_rate`,
  `riebesell`, `tpl_ilf`, `camera_rate`) do not, since they aren't
  currency values. Summary totals can therefore differ by a penny or two
  from what you'd get rounding only once at the very end — a known,
  accepted trade-off, not a bug.

## Testing

`test/test.py` runs plain-assert smoke tests against every function in
`core/library.py`, including edge cases (empty camera lists, `None`
handling, all-`None` sums) and the `resolve()` graph engine, checked
against hand-calculated figures from the original workbook.