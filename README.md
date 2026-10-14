# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are built now, so that last command runs the full agent.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

You tell FitFindr what you want in plain words, like "a vintage graphic tee under $30, size M". It searches 40 sample listings, picks the best match, suggests one or two outfits using the wardrobe you give it, and writes a short caption you could actually post. If nothing matches, it stops early and tells you what to change instead of making something up.

---

## Tool Inventory

### `search_listings`

- **What it does:** Looks through the 40 listings for items that match a few keywords, and optionally a size and a price ceiling.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None). A size or price of None means skip that filter.
- **Returns:** A list of listing dicts, best match first, at most `config.SEARCH_RESULT_LIMIT` long. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None) and `platform`. Best match means the most query words found as whole words in the title, description and style tags. Ties go to the cheaper listing. Listings that match no words are dropped. The price filter is inclusive. The size filter splits the listing's size on spaces, slashes and parentheses and checks if the requested size is one of the pieces, ignoring case. So "M" matches `M`, `S/M` and `M/L`, "L" does not match `XL`, and "One Size", waist sizes and shoe sizes never match a letter size.
- **When it has nothing:** An empty list `[]`. Never None and never an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the thrifted item, using the user's wardrobe when there is one.
- **Inputs:** `new_item` (dict, one listing as returned by `search_listings`), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts).
- **Returns:** A non-empty string with the outfit suggestions. When the wardrobe has items, the text names specific pieces the user already owns.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns general styling advice for the item, still a non-empty string. It does not raise and it does not return an empty string.

### `create_fit_card`

- **What it does:** Asks the model to write a short caption, like someone would post, about the find.
- **Inputs:** `outfit` (str, the text from `suggest_outfit`), `new_item` (dict, the same listing).
- **Returns:** A string of two to four sentences that mentions the item, its price and its platform once each. The wording changes from run to run.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns a plain message saying there was no outfit to write about. It does not call the model and it does not raise.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that tells the user what to change (raise the price, drop the size, or use fewer keywords), leave `session["fit_card"]` as None, and stop. Otherwise take the first result, put it in `session["selected_item"]`, and go on to `suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Plain regex and string splitting, no model call, in `agent.py::_parse_query`. A price comes from phrases like "under $30" or "max $30", or from any bare "$30" if no phrase matches. A size comes from "size M". Whatever text is left becomes the description. The parser does not strip filler words like "looking for", "a" and "the". `search_listings` ignores them when it scores keywords.

**What moves through the session:** `query`, then `parsed`, then `search_results`, then `selected_item`, then `outfit_suggestion`, then `fit_card`. `error` is only set when the run stops early. Each tool reads its input back out of the session instead of taking the previous tool's return value directly.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Buy it. At eighteen dollars, it is a versatile Y2K staple that balances your closet. 

Outfit one: Pair the butterfly baby tee with your baggy straight-leg dark wash jeans. Add the black cropped zip hoodie layered open on top, and finish with your chunky white sneakers and black crossbody bag for an effortless streetwear contrast. 

Outfit two: Tuck the tee into your wide-leg khaki trousers. Layer the vintage black denim jacket over your shoulders, wear the brown leather belt to tie in the earth tones, and step into your black combat boots to grunge up the sweet butterfly print. Both looks lean into your existing pieces while letting the tee pop.

  Fit card: Manifesting warm weather with this little Y2K butterfly tee. It is giving sweet fairy vibes balanced out with total everyday wearability, and it can be yours on Depop for just 18 dollars. Style it with baggy denim and a zip hoodie or tuck it into trousers for the ultimate early 2000s moment.

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', size='M', max_price=30))"
[{'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit, search_listings; from utils.data_loader import get_example_wardrobe; item = search_listings('graphic tee', size='M', max_price=30)[0]; print(suggest_outfit(item, get_example_wardrobe()))"
Buy it. Fifteen dollars is a great price for a versatile layering piece in excellent condition.

Outfit one: Grunge streetwear. Layer the mesh top underneath your white ribbed tank top, paired with your baggy straight-leg dark wash jeans. Finish with your black combat boots and black crossbody bag for a textured, 2000s-inspired look.

Outfit two: Edgy minimal. Wear the mesh top under your oversized grey crewneck sweatshirt so the sheer sleeves peek out at the wrists, paired with your wide-leg khaki trousers. Add your chunky white sneakers and the black crossbody bag for contrast.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats a broken-in pair of vintage Levi's 501s with your favorite white sneakers for that effortless 90s off-duty look. These have the absolute best medium wash and sit just right on the waist. Grab them for thirty eight dollars over on my depop before someone else snags your new favorite denim.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I searched the data file for every size in the 40 listings and gave Claude that list, then asked it to build `search_listings` from my spec.
- *What came back:* A size filter that splits the listing's size on spaces, slashes and parentheses and checks if the requested size is one of the pieces. The data has sizes like `S/M`, `XL (oversized)`, `W28` and `US 8.5`, and a plain substring check would match the L in XL.
- *What I changed:* I kept that approach and wrote the exact rule into the Tool Inventory so the spec and the code say the same thing. I tested it with `graphic tee`, size M, under $30. It returned two `S/M` listings and left out the L bootleg tee.

**Moment 2**

- *What I asked for:* I asked Claude to build `create_fit_card`, then ran it three times on the same item to check that the captions differ.
- *What came back:* Three word-for-word identical captions, even though `TEMPERATURE` in `config.py` was already 0.9.
- *What I changed:* The cause was `CACHE_ENABLED`, which reuses an answer to an identical prompt. I turned the cache off for that one test by setting `AI201_CACHE` to 0 and the three captions came out different. I did not change any tool code. The cache stays on while I build.

**Moment 3**

- *What I asked for:* I had Claude Code score criterion 5 against the before run log, strictly.
- *What came back:* It first marked criterion 5 FAIL, because the trace only prints the first 3
  titles of each result list and never shows every listing's price, so there was no way to prove
  the ceiling held for a whole result set from that log alone.
- *What I changed:* I decided missing evidence is not the same thing as a real failure. Instead of
  accepting the FAIL or just assuming it was fine, I had it write `check_ceiling.py`, a small
  script that calls `search_listings()` directly, no model, for the same 5 queries, and prints
  every returned listing's id, title and price. It came back 5 of 5, every listing under its
  ceiling, so I changed the verdict to MET on real evidence instead of a guess either way.

**Moment 4**

- *What I asked for:* Nothing, this one was me catching myself. I was looking at the
  "vintage denim jacket under $40" search and got suspicious, because high-waisted denim cutoff
  shorts ranked first instead of a jacket.
- *What came back:* I checked the actual listing data instead of assuming the search was broken.
  The jacket in the data costs $42, which is over the $40 ceiling, so the search was right to drop
  it and rank the shorts first, since the shorts fit the price and still matched on "denim."
- *What I changed:* Nothing in the code. I almost treated this as a bug and nearly used it as my
  one improvement, but it was the price filter doing exactly what it is supposed to do. I used the
  fit card price format instead, since that one was a real, measured problem.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches what suggest_outfit gets | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5)* |
| 4. Fit card reads like a short post and has the facts | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling holds | 5 of 5 queries | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

\* I checked `session["selected_item"]` against the input to `suggest_outfit` by title, price and
platform, since that is all the trace records. I wrote a one line check straight after this table
on exactly what that does and does not prove about `id`.

For criterion 5, "Try 1" through "Try 5" are the 5 different queries the criterion asks for
(`silk slip dress`, `platform sneakers`, `track jacket`, `leather jacket`, `band tee`), not 5
repeats of one query — search is plain code with no model involved, so repeating one query would
not have told me anything new. I first marked this row FAIL because the trace only prints the
first 3 titles of each result list, not every listing's price. I wrote `check_ceiling.py` to call
`search_listings()` directly for these same 5 queries and print every returned listing's id, title
and price. Its output is pasted below the table. All 5 queries pass with no exceptions, so I am
changing this row to MET.

**Real output from one try per criterion**, pasted as text, naming the file and function
that produced it. The trace lines come from `trace.step()` calls inside `agent.py::run_agent`;
the session fields and fit card/outfit text come from the same run, captured by
`run_eval.py::run_once`.

Criterion 1 — `matching query completes`, Try 1 (`agent.py::run_agent`, trace via `trace.step()`):

```
[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[2] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Buy it. At eighteen dollars, it is a versatile Y2K staple.   Outfit one leans into vintage streetwear contrast…
[3] create_fit_card
      in:  item='Y2K Baby Tee — Butterfly Print' ($18.0), outfit='Buy it. At eighteen dollars, it is a versatile Y2K stap…
      out: Found the ultimate Y2K baby tee with the cutest pastel butterfly print for just eighteen dollars on depop. It …
```

Criterion 2 — `impossible query stops early`, Try 1 (`agent.py::run_agent`, the empty-search branch):

```
- stopped early: yes — Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby size, or use fewer or different keywords (for example 'tee' instead of 'graphic t-shirt').

[1] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
[2] empty search
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby …
      →    branch: empty, stopping
```

Criterion 3 — `selected item matches what suggest_outfit gets`, Try 1 (`agent.py::run_agent`, session vs. trace input):

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)

[2] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
```

On criterion 3, what I checked and what I did not: in `agent.py::run_agent`, line 178 sets
`session["selected_item"] = session["search_results"][0]`, which stores the whole listing dict,
id field included, not a separately pulled out id. Line 181 then calls
`suggest_outfit(session["selected_item"], session["wardrobe"])`, passing that exact same dict
object straight through, so the id going into `suggest_outfit` is not just equal, it is the same
object in memory as `session["selected_item"]`. I read these two lines and did not change them. I
did not independently print the `id` field anywhere in the trace or the run log, so my PASS marks
above rest on title, price and platform matching, plus this read of the code, not on an id value
I actually saw printed.

Criterion 4 — `fit card reads like a short post`, Try 1 (`tools.py::create_fit_card`, captured by `run_eval.py::run_once`):

```
Live out your early 2000s pop star dreams in this pastel butterfly baby tee, priced at just $18 on Depop. Throw it on with baggy jeans and beat-up boots to nail that sweet-meets-edgy look. It is seriously the easiest way to add a little retro magic to your everyday rotation.
```

Criterion 5 — `price ceiling — silk slip dress`, Try 1 (`agent.py::run_agent`, trace via `trace.step()`):

```
[1] search_listings (via MCP)
      in:  description='silk slip dress in midi length', size=None, max_price=40.0
      out: 5 items: 90s Silk Slip Dress — Floral, Midi Length, Y2K Baby Tee — Butterfly Print, High-Waisted Denim Shorts — Cutoff … +2 more
```

The trace line above only shows the first 3 titles of the result list and does not show every
listing's price, so it cannot prove the ceiling holds for a whole result set by itself. I wrote
`check_ceiling.py`, which calls `search_listings()` directly, no model involved, for the same 5
queries the trace showed above, and prints every returned listing's id, title and price. Full
output from `python check_ceiling.py`, labeled `check_ceiling.py`:

```
query: description='silk slip dress in midi length', size=None, max_price=40.0
  id=lst_013  price=$30.0  title=90s Silk Slip Dress — Floral, Midi Length
  id=lst_002  price=$18.0  title=Y2K Baby Tee — Butterfly Print
  id=lst_016  price=$24.0  title=High-Waisted Denim Shorts — Cutoff
  id=lst_029  price=$28.0  title=Silk Button-Down — Sage Green
  id=lst_037  price=$30.0  title=Straight Leg Black Jeans — Faded
  PASS

query: description='platform sneakers', size=None, max_price=60.0
  id=lst_019  price=$48.0  title=Platform Sneakers — White Chunky Sole
  id=lst_035  price=$20.0  title=Low-Top Canvas Sneakers — Off-White
  id=lst_009  price=$55.0  title=Platform Mary Janes — Black Patent
  PASS

query: description='90s track jacket', size=None, max_price=45.0
  id=lst_004  price=$45.0  title=90s Track Jacket — Navy/White Stripe
  id=lst_034  price=$14.0  title=Bucket Hat — Reversible, Brown Plaid
  id=lst_013  price=$30.0  title=90s Silk Slip Dress — Floral, Midi Length
  id=lst_032  price=$33.0  title=Shacket — Olive Canvas
  id=lst_031  price=$36.0  title=Baggy Carpenter Jeans — Dark Wash
  id=lst_010  price=$40.0  title=Vintage Windbreaker — Color Block Purple/Teal
  id=lst_007  price=$42.0  title=Denim Jacket — Light Wash, Cropped
  PASS

query: description='leather jacket', size=None, max_price=100.0
  id=lst_022  price=$75.0  title=90s Leather Bomber — Black
  id=lst_014  price=$12.0  title=Leather Belt — Brown, Braided
  id=lst_032  price=$33.0  title=Shacket — Olive Canvas
  id=lst_039  price=$38.0  title=Mini Shoulder Bag — Tan Leather
  id=lst_007  price=$42.0  title=Denim Jacket — Light Wash, Cropped
  id=lst_004  price=$45.0  title=90s Track Jacket — Navy/White Stripe
  id=lst_009  price=$55.0  title=Platform Mary Janes — Black Patent
  PASS

query: description='band tee', size=None, max_price=20.0
  id=lst_033  price=$19.0  title=Vintage Band Tee — Faded Grey
  id=lst_017  price=$15.0  title=Mesh Long-Sleeve Top — Black
  id=lst_002  price=$18.0  title=Y2K Baby Tee — Butterfly Print
  PASS
```

Every listing in every one of the 5 queries comes back at or under its max_price, so criterion 5
is MET at 5 of 5 queries.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | Read the trace for each try in `matching query completes`. All 5 showed the search, suggest_outfit and create_fit_card steps and a non-null fit card. |
| 2 | Impossible query stops before the second tool | 5 of 5 | MET (5/5) | Read the trace for each try in `impossible query stops early`. All 5 stopped after the empty search step, before suggest_outfit, with a message naming what to change. |
| 3 | Selected item matches what suggest_outfit gets | 5 of 5 | MET (5/5) | Compared `session["selected_item"]` to the suggest_outfit trace input by title, price and platform for all 5 tries, and read the two agent.py lines that make it the same object. |
| 4 | Fit card reads like a short post and has the facts | 4 of 5 | MET (5/5) | All 5 fit cards in `fit card reads like a short post` were 2 to 4 sentences, named the price in some form and named the platform. |
| 5 | The price ceiling holds | 5 of 5 queries | MET (5/5) | `check_ceiling.py` ran all 5 queries straight against search_listings, no model, and printed every returned listing's price. None went over its ceiling. |

I am being honest about this: all 5 criteria came back MET, none missed, which means my unit 3 targets were too easy. I set them low enough that I could not fail even on the parts of the loop that depend on the model, where I expected some real variance.

**Where I would tighten a target:**

Criterion 4 is the one I would tighten first. I wrote the target as "at least 4 of the 5 captions," expecting the model to sometimes skip the price or the platform or run long. Instead all 5 of 5 captions hit the length and both facts, and I counted the full run: of 45 fit cards produced across every scenario in the before run, 11 wrote the price as digits with a dollar sign like $18, and 34 spelled it out, as "eighteen dollars" or "18 dollars." All 45 named the platform. The target let spelled-out prices count as a pass, so it never caught how inconsistent the price format actually is. I would tighten criterion 4 to require the price written as $N, digits and a dollar sign, and the platform named, in every card, 5 of 5, not 4 of 5.

Criterion 1 at "4 of 5" was also low. I picked that number expecting occasional model failures on the outfit or caption call, but across the whole before run every matching query that reached the model completed all three tools. 4 of 5 gave myself a miss I never used.

**Gaps I found and closed, not misses:**

Criterion 3's target was already met, but the way I was checking it had a gap. The trace and session only show title, price and platform, not the listing's `id` field the criterion names. I read the two relevant lines in `agent.py::run_agent` and confirmed `session["selected_item"]` is the whole listing dict, id included, and that the same dict object, not a copy, gets passed into `suggest_outfit`. That closes the gap by reading the code, since the id itself is never printed anywhere in the log.

Criterion 5's target was also already met, but the trace line for each query only prints the first 3 titles of the result list and never shows every returned listing's price, so it could not prove the ceiling held for a full result set. I wrote `check_ceiling.py` to call `search_listings()` directly for the same 5 queries, print every result's id, title and price, and check each against its max_price. All 5 queries passed with no exceptions, and now I have real evidence instead of a trace that just doesn't show enough.

**One observation, not a miss:**

Reading the trace, `search_listings` sometimes returns loosely related items, for example a bucket hat and a silk slip dress show up in the results for "90s track jacket." The keyword scoring in `tools.py` pulls in anything that shares even one non-filler word with the query, including things that are not jackets at all. This never changed an outcome in this run, because the right item ranked first every time and that is the one `session["selected_item"]` picked up, but it is worth watching if a future query's best match is not the first thing a person would pick.

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[2] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Buy it. At eighteen dollars, it is a versatile Y2K staple that balances your closet.   Outfit one: Pair the bu…
[3] create_fit_card
      in:  item='Y2K Baby Tee — Butterfly Print' ($18.0), outfit='Buy it. At eighteen dollars, it is a versatile Y2K stap…
      out: This Y2K butterfly baby tee is the sweetest little pastel graphic for your collection. It is up on Depop right…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Buy it. At eighteen dollars, it is a versatile Y2K staple that balances your closet. 

Outfit one: Pair the butterfly baby tee with your baggy straight-leg dark wash jeans. Add the black cropped zip hoodie layered open on top, and finish with your chunky white sneakers and black crossbody bag for an effortless streetwear contrast. 

Outfit two: Tuck the tee into your wide-leg khaki trousers. Layer the vintage black denim jacket over your shoulders, wear the brown leather belt to tie in the earth tones, and step into your black combat boots to grunge up the sweet butterfly print. Both looks lean into your existing pieces while letting the tee pop.

  Fit card: This Y2K butterfly baby tee is the sweetest little pastel graphic for your collection. It is up on Depop right now for $18 and instantly adds that nostalgic early 2000s energy to any outfit. Layer it under a baggy zip hoodie or toughen it up with wide-leg cargos.

0 model calls this session, 2 served from cache
```

Step 1 in that trace, `search_listings (via MCP)`, is the search_listings call going through MCP, not a direct function call.

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
[2] empty search
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby …
      →    branch: empty, stopping

  Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby size, or use fewer or different keywords (for example 'tee' instead of 'graphic t-shirt').

0 model calls this session
```

**On the MCP move:** `search_listings` is registered as a tool in `mcp_server.py`, wrapped around
the same function from `tools.py`. `agent.py::run_agent` no longer calls `search_listings()`
directly, it calls `mcp_client.call_tool("search_listings", tool_inputs)` instead, which is the
line the trace labels `search_listings (via MCP)`. The results came back identical to before the
move, same items, same order, same prices, so the rewire did not change what the tool returns,
only how the loop reaches it.

---

## Failure Modes

**Empty search.** I triggered this with the query `designer ballgown size XXS under $5`, which
nothing in the data matches. The agent showed:

```
Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby size, or use fewer or different keywords (for example 'tee' instead of 'graphic t-shirt').
```

**Empty wardrobe.** I ran `python app.py ask 'denim jacket under $50' --empty-wardrobe`. With
nothing in the wardrobe, `suggest_outfit` falls back to general styling advice instead of naming
specific pieces the person owns. The outfit advice it gave:

```
Buy it. For a casual streetwear look, layer this cropped Wrangler jacket over an oversized black graphic t-shirt, high-waisted black biker shorts, and chunky white sneakers. Add a silver chain necklace to finish the outfit. Alternatively, lean into the vintage vibe for brunch by pairing it with a floral midi slip dress in a dark maroon or emerald shade, paired with beat-up canvas high-top sneakers and a structured canvas tote bag. The light wash denim provides a great casual contrast to both fitted and flowing textures.
```

**Model unavailable.** I triggered this by changing one character of `GEMINI_API_KEY` in `.env`
and running a fresh query. I did not do this again for this write-up since I already have the
exact message from the code, and I did not want to touch the key a second time. `generate.py`
catches the provider's error, and since a bad key is not a rate limit, it raises
`ModelUnavailable(_explain(exc))`. `_explain()` checks for "api key" in the error text and returns:

```
The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

`agent.py` imports `ModelUnavailable` but does not catch it itself, so it goes up to
`app.py::main()`, which catches any exception and prints `f"{type(exc).__name__}: {exc}"` to
stderr, no stack trace. So the actual printed line is:

```
ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

Honestly, that is not a clean message, it leaks the raw Python class name `ModelUnavailable` right
at the front. It is still a lot better than a stack trace, and someone reading it can tell
something is wrong with the key without digging through a traceback, but it is not the polished,
person-facing message the exercise probably wants. A real fix would catch `ModelUnavailable`
somewhere in `agent.py` or `app.py::cmd_ask` and print just the message, not `type(exc).__name__`.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

I changed the `create_fit_card` prompt in `tools.py`, nothing else. Before:

```
"Rules: two to four sentences. Mention the item, its price and the "
"platform once each. Be specific about the vibe. Plain text, no "
"markdown, no hashtag pile."
```

After:

```
"Rules: two to four sentences. Mention the item, its price and the "
"platform once each. Write the price as digits with a dollar sign, "
"like $18, never spelled out as words. Name the platform by name. "
"Be specific about the vibe. Plain text, no markdown, no hashtag "
"pile."
```

**Why I picked this:** going back through the before run, 34 of the 45 fit cards it produced spelled the price out as words, like "eighteen dollars" or "18 dollars," and only 11 wrote it as $N digits. Every card still named the platform, so that half of criterion 4 was never the problem. The old prompt just said "mention the price" and left the format up to the model, so the model did whatever sounded more natural in the sentence, which was usually words. I did not touch `agent.py`, `mcp_server.py`, `scenarios.py` or the loop. This is a model instruction, not a code fix, since the price format lives in text the model writes, not in a calculation anywhere in the loop.

**Which failure it was meant to fix:** criterion 4 never technically failed at its target of 4 of 5, but I was tightening it to 5 of 5 with the price written as $N specifically, and the old prompt would not have hit that stricter bar.

**Price format, before vs after, counted across all 45 fit cards in each run:**

| | Price as $N digits | Price spelled out | No price at all | Platform named |
|---|---|---|---|---|
| Before | 11 of 45 | 34 of 45 | 0 of 45 | 45 of 45 |
| After | 45 of 45 | 0 of 45 | 0 of 45 | 45 of 45 |

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches what suggest_outfit gets | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5)* |
| 4. Fit card reads like a short post and has the facts | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling holds | 5 of 5 queries | PASS | PASS | PASS | PASS | PASS | MET (5/5)** |

\* Same caveat as the before run. Title, price and platform match between `session["selected_item"]`
and the `suggest_outfit` call for all 5 tries, but that is not a literal `id` field.

\*\* Search is plain code, no model, and I did not touch `tools.py::search_listings` or the data,
so the same 5 queries return the exact same listings as the before run. I did not rerun
`check_ceiling.py` for this, I confirmed from the after log that each query's selected item
(the first, cheapest-ranked result) is still at or under its max_price, same as before, and that
check_ceiling.py's earlier full result still applies since nothing underneath it changed.

**Real output, one try per criterion, named by file and function:**

Criterion 1, Try 1 (`tools.py::create_fit_card`, via `agent.py::run_agent`, captured by `run_eval.py::run_once`):

```
This dreamy little butterfly baby tee is giving major early 2000s mall goth energy. I am asking $18 for it and it is currently listed on Depop. Grab it before I change my mind and keep it for myself.
```

Criterion 2, Try 1 (`agent.py::run_agent`, the empty-search branch, trace via `trace.step()`):

```
[2] empty search
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: Nothing matched 'designer ballgown'. Try to raise your price limit above $5, or drop size XXS or try a nearby …
      →    branch: empty, stopping
```

Criterion 3, Try 1 (`agent.py::run_agent`, session vs. trace input):

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)

[2] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
```

Criterion 4, Try 1 (`tools.py::create_fit_card`, captured by `run_eval.py::run_once`):

```
Found this pastel butterfly baby tee thrifting and honestly need to keep it for myself. It gives major Y2K mall rat energy and is super easy to style with baggy denim or wide-leg trousers. Grab it on Depop for $18 before I change my mind.
```

Criterion 5, Try 1 (`agent.py::run_agent`, session, `price ceiling — silk slip dress`):

```
- selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
```
This item's $30 price is under its $40 ceiling. `check_ceiling.py` already confirmed every other
listing in this query's result set is $30 or less too.

**Did it help, and how do I know:**

Yes, it helped, and I know because I counted every fit card in the after run by hand the same way I counted the before run: 45 of 45 cards now write the price as $N digits, up from 11 of 45 before, and 0 of 45 spell it out, down from 34 of 45. Platform naming did not need fixing and stayed at 45 of 45 in both runs. I did not find a single card in the after run that still spelled out the price or dropped it entirely, so there is nothing to walk back here. I am being honest that this was a one-dimensional fix on a criterion that was already passing. It did not change whether criterion 4 was MET, it made the MET harder to argue with.


---

## What's Still Broken

No criterion is missed right now, all 5 came back MET in both the before and after run, so there
is nothing here that is a failing number. There is still real stuff left unfixed though.

**search_listings pulls in loosely related items.** Reading the trace, a query like "90s track
jacket" returns a bucket hat and a silk slip dress in its result list, because the keyword scoring
in `tools.py::search_listings` counts any shared non-filler word, and style tags like "90s" or
"vintage" show up on all kinds of unrelated listings. I would tighten this by requiring more of
the query's words to match, not just one, so a bucket hat sharing only the word "90s" with the
query would not make the cut. I stopped here and used the fit card price format as my one
improvement instead, because this never actually changed an outcome. The right item ranked first
in every single try across both runs, since the scoring sorts by match count and then by price,
and `session["selected_item"]` always takes the first result. So the loose matches sit lower in
the list where nothing in the loop ever reads them. The unit allows one change and I picked the
one that was actually causing a measurable problem.

**Criterion 3 is verified by reading code, not by output.** The trace and the run log never print
a listing's `id` field anywhere, only title, price and platform. I confirmed `session["selected_item"]`
and the input to `suggest_outfit` are the same object by reading the two lines in
`agent.py::run_agent` that do it, not by seeing an id printed and compared. That is a real gap in
what the trace shows, not in what the code does. If I wanted this criterion machine checkable
without reading code every time, I would add the id to the trace step's input, since right now
nobody rerunning this later can confirm it from the log alone.

**The fit card price fix is a model instruction, not a code rule.** `create_fit_card`'s new prompt
tells the model to write the price as $N and it did so in all 45 cards in the after run, but
nothing in `tools.py` checks or corrects the model's output if it ignores that instruction on some
future run. The before run showed the model will drift toward spelling things out when the prompt
does not say otherwise, so I would not be surprised if a different temperature or a different item
produced a spelled-out price again. If I wanted this enforced for real, I would check the string
for a `$` pattern after `generate()` returns and only then would I trust it unconditionally.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
