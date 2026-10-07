# Data notes

Things I found reading data/listings.json before building search_listings.

- 40 listings, 10 wardrobe items.
- Fields I can filter on: title, description, category, style_tags, size, condition, price, colors, brand, platform.
- price is a float, so max_price can be compared directly.
- brand can be null. Anything that uses brand has to handle that.
- size is a string and it's messy. Five formats show up:
  - plain letters: S, M, L, XL
  - ranges: S/M, M/L, L/XL
  - letters with a note: XL (oversized), XL (fits oversized)
  - waist and shoe sizes: W28, US 8.5
  - one size: One Size, One Size (adjustable)
- A plain == check on "M" would miss S/M and M/L. A substring check would match the L inside XL. Plan is to split the size into tokens and check if the requested size is one of them.
- Words like "vintage" and "graphic" live in title, description and style_tags, so the keyword search has to look in all three.
