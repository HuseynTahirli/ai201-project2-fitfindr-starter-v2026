"""
Criterion 5 check, direct and model-free.

Calls search_listings() straight, with the same description, size and
max_price the trace showed for each of the five price-ceiling scenarios in
scenarios.py. Prints every returned listing's id, title and price, then
PASS if all of them are at or under max_price, else FAIL naming the
offending listing.

    python check_ceiling.py
"""

from tools import search_listings

QUERIES = [
    {"description": "silk slip dress in midi length", "size": None, "max_price": 40.0},
    {"description": "platform sneakers", "size": None, "max_price": 60.0},
    {"description": "90s track jacket", "size": None, "max_price": 45.0},
    {"description": "leather jacket", "size": None, "max_price": 100.0},
    {"description": "band tee", "size": None, "max_price": 20.0},
]


def main() -> None:
    for query in QUERIES:
        print(f"query: description={query['description']!r}, size={query['size']!r}, max_price={query['max_price']!r}")
        results = search_listings(query["description"], query["size"], query["max_price"])

        if not results:
            print("  (no results)")
            print("  PASS\n")
            continue

        offenders = []
        for item in results:
            print(f"  id={item.get('id')}  price=${item.get('price')}  title={item.get('title')}")
            if item.get("price") > query["max_price"]:
                offenders.append(item)

        if offenders:
            print("  FAIL")
            for item in offenders:
                print(f"    offending listing: id={item.get('id')}, title={item.get('title')!r}, price=${item.get('price')}")
        else:
            print("  PASS")
        print()


if __name__ == "__main__":
    main()
