"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # A normal matching query. Criterion 3 — the item passed into
        # suggest_outfit must be the same item session["selected_item"] holds.
        "name": "selected item matches what suggest_outfit gets",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # The same matching query, run_eval.py's 5 tries give us 5 fit cards
        # on the same item (search is plain code, so the first result is
        # deterministic). Criterion 4 — fit card length and facts.
        "name": "fit card reads like a short post",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5 needs 5 DIFFERENT queries that each include a max price —
    # not 5 tries of the same one — so it gets five scenarios of its own.
    {
        "name": "price ceiling — silk slip dress",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price ceiling — platform sneakers",
        "query": "platform sneakers under $60",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price ceiling — track jacket",
        "query": "90s track jacket under $45",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price ceiling — leather jacket",
        "query": "leather jacket under $100",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price ceiling — band tee",
        "query": "band tee under $20",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
