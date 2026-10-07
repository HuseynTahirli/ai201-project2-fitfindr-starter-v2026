"""
The three FitFindr tools.

    search_listings(description, size, max_price)  -> list[dict]
    suggest_outfit(new_item, wardrobe)             -> str
    create_fit_card(outfit, new_item)              -> str
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings

# Words that say nothing about the item. Dropped before scoring.
_FILLER = {
    "a", "an", "the", "for", "and", "in", "with", "size", "under", "below",
    "max", "looking", "want", "find", "me", "i", "some", "something", "to",
    "of", "on", "my",
}


def _words(text) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _size_matches(requested: str, listing_size) -> bool:
    """
    True if the requested size is a whole piece of the listing's size.
    "M" matches "M", "S/M" and "M/L". "L" does not match "XL".
    """
    req = requested.strip().lower()
    have = (listing_size or "").strip().lower()
    if not req or req == have:
        return True
    return req in re.split(r"[\s/()]+", have)


def _price_text(price) -> str:
    if price is None:
        return "unknown price"
    if float(price) == int(price):
        return f"${int(price)}"
    return f"${price:.2f}"


def _describe_item(item: dict) -> str:
    lines = [
        f"Title: {item.get('title')}",
        f"Category: {item.get('category')}",
        f"Colors: {', '.join(item.get('colors') or [])}",
        f"Style tags: {', '.join(item.get('style_tags') or [])}",
        f"Size: {item.get('size')}",
        f"Condition: {item.get('condition')}",
        f"Price: {_price_text(item.get('price'))}",
        f"Platform: {item.get('platform')}",
    ]
    if item.get("brand"):
        lines.append(f"Brand: {item['brand']}")
    return "\n".join(lines)


# -- Tool 1: search_listings ---------------------------------------------------

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Returns matching listing dicts, best match first (most query words found
    as whole words in title, description and style tags, cheaper wins ties),
    at most config.SEARCH_RESULT_LIMIT. Returns [] when nothing matches.
    """
    query = {w for w in _words(description) if w not in _FILLER}
    scored = []

    for item in load_listings():
        if max_price is not None and item["price"] > max_price:
            continue
        if size and not _size_matches(size, item.get("size")):
            continue

        text = " ".join([
            item.get("title") or "",
            item.get("description") or "",
            " ".join(item.get("style_tags") or []),
        ])
        score = len(query & set(_words(text)))
        if score == 0:
            continue
        scored.append((score, item))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [item for _, item in scored[: config.SEARCH_RESULT_LIMIT]]


# -- Tool 2: suggest_outfit ----------------------------------------------------

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    One or two outfit ideas built around new_item. Names pieces from the
    wardrobe when there are any. With an empty wardrobe, gives general
    styling advice. Always returns a non-empty string.
    """
    items = (wardrobe or {}).get("items") or []

    system = (
        "You are a thrift stylist. Be specific and practical. "
        "Plain text only, no markdown, under 120 words."
    )

    if not items:
        prompt = (
            "Someone is thinking about buying this secondhand piece:\n\n"
            f"{_describe_item(new_item)}\n\n"
            "They did not tell me what they own. Give one or two general "
            "outfit ideas for this piece, naming the kinds of items that "
            "would go with it."
        )
    else:
        lines = []
        for w in items:
            line = (
                f"- {w.get('name')} ({w.get('category')}; colors: "
                f"{', '.join(w.get('colors') or [])}; tags: "
                f"{', '.join(w.get('style_tags') or [])})"
            )
            if w.get("notes"):
                line += f" - {w['notes']}"
            lines.append(line)
        prompt = (
            "Someone is thinking about buying this secondhand piece:\n\n"
            f"{_describe_item(new_item)}\n\n"
            "Here is what they already own:\n"
            + "\n".join(lines)
            + "\n\nGive one or two outfits. Each outfit must name specific "
            "pieces from their wardrobe by name, plus the new piece."
        )

    text = generate(prompt, system=system)
    if not text.strip():
        return "The model came back empty, so there are no outfit ideas for this item yet."
    return text


# -- Tool 3: create_fit_card ---------------------------------------------------

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    A two-to-four sentence caption someone would post. If outfit is empty or
    whitespace, returns a plain message and does not call the model.
    """
    if not outfit or not outfit.strip():
        return "There was no outfit to write a caption about."

    system = (
        "You write short social media captions for thrift finds. "
        "Sound like a real person posting, not a product listing."
    )
    prompt = (
        "Write a caption for this thrift find.\n\n"
        f"{_describe_item(new_item)}\n\n"
        f"The outfit idea:\n{outfit}\n\n"
        "Rules: two to four sentences. Mention the item, its price and the "
        "platform once each. Be specific about the vibe. Plain text, no "
        "markdown, no hashtag pile."
    )
    return generate(prompt, system=system)
