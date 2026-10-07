# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 and not 5 of 5 because my search is a plain whole-word keyword match, so a phrasing like "t-shirt" will miss a listing titled "tee". Two of the three tools also call a model, and a model call can fail or time out once in a while.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I picked 5 of 5 here because this path never depends on the model. Search is plain code, so an impossible query gives an empty list every time, and the branch checks for it before anything else runs. If this ever misses, the loop is wrong, not unlucky.

---

## 3. The item search found is the item the next tool gets

In every run that gets past the search, the id in `session["selected_item"]` matches the id of the item `suggest_outfit` was actually called with, checked by recording the argument at the call. 5 of 5 tries.

**Why this target:**
No model is involved in passing the item along. It is a dict going into the session and coming back out, so there is nothing random to blame. If this misses even once, it is a real bug in my loop and not noise, so I am not allowing a miss.

---

## 4. The fit card reads like a short post and has the facts

Run `create_fit_card` 5 times on the same item. At least 4 of the 5 captions are 2 to 4 sentences long and mention both the price and the platform.

**Why this target:**
The model words things differently every run, so I can't check exact words. Length, price and platform are things I can see just by looking. I picked 4 of 5 and not 5 of 5 because a model sometimes ignores an instruction, and counting sentences gets fuzzy with things like "$24." or exclamation marks.

---

## 5. The price ceiling holds

For 5 different queries that each include a max price, every listing returned costs at most that price. 5 of 5 queries.

**Why this target:**
Price is a float in the data and the filter is a plain less-than-or-equal comparison, with no model and nothing fuzzy. If one listing over the ceiling gets through, it is a bug. The other risk is the query parser reading the number wrong from phrases like "under $30" or "$30 max", which is why I picked this one.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
