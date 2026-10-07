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
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
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

**How the query is parsed:** Plain regex and string splitting, no model call. A price comes from phrases like "under $30" or "$30 max". A size comes from "size M". Whatever is left, minus filler words like "looking for", "a" and "the", becomes the description.

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
