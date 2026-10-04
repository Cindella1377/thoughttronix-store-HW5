# PRD: The ThoughtTronix Store — Product Photos

*Commissioned by ThoughtTronix Product Management. "Your Thoughts, Our Business."*

*Builds on `prd/core-platform.md`. Where this document is silent, the core PRD's conventions hold.*

---

## Problem Statement

The catalog sells thirty-odd devices and shows a photograph of none of them. Every product wears its category's placeholder illustration, so a Seraphine and a Seraphine Wall Mount look identical until the customer reads the name. Customers are being asked to put our hardware in their homes, and in several cases their heads, sight unseen.

The Creative department has delivered photography for twelve products. The store has nowhere to put it: `Product` has no image field, the project has no media handling, and staff have no way to attach a photo to anything.

We need products that can carry a real photo, a back office where staff manage those photos, and a dependable fallback so a product without a photo still looks designed.

## Solution

**Real photos.** A product may have one photo. The catalog card, the product page, and the back office show it wherever the product's image appears.

**The baseline placeholder.** A product with no photo shows what every product shows today: its category's placeholder illustration, with `default.svg` for categories that have none. The existing artwork is the baseline; nothing about it changes.

**Staff control.** Staff upload, replace, or clear a product's photo from the product form. Clearing a photo returns the product to its placeholder.

**The demo world.** The seed command attaches the twelve delivered photos to the products they depict, so a fresh clone shows both halves of the feature at once.

## User Stories

**Customer**

1. As a customer, a product with a photo shows that photo on its catalog card and on its product page.
2. As a customer, a product without a photo shows its category's placeholder illustration, never a broken image or an empty box.
3. As a customer, every catalog card has the same square image area, so the grid stays even whether a card holds a portrait photo or a landscape placeholder.
4. As a customer, the product page shows the whole photo, uncropped.

**Employee (staff)**

5. As an employee, I can upload a photo when creating or editing a product.
6. As an employee, I can replace a product's photo, or clear it so the product goes back to its placeholder.
7. As an employee, the edit form shows me the image the product currently displays, photo or placeholder.
8. As an employee, the form rejects a file that is not an image and a file larger than 2 MB, with a message that says which rule was broken.
9. As an employee, the product list shows a small thumbnail beside each product, so I can see at a glance which products still need a photo.

**Any developer**

10. As a developer, `seed` gives twelve products their photos and leaves the rest on placeholders, and running it twice leaves no leftover files.
11. As a developer, the app still runs with no `.env` and no `media/` folder present.

## Implementation Decisions

**The field.** `Product.image = models.ImageField(upload_to="products/", blank=True)`. One photo per product; no gallery, no second "poster" image. Pillow becomes a dependency.

**One place decides what to show.** `Product.image_url` (a property) returns the uploaded photo's URL when `image` is set, otherwise the static URL of `category.placeholder_image`. Every template uses `product.image_url`; no template repeats the "photo or placeholder" choice. `Category.placeholder_image` and `PLACEHOLDER_CATEGORIES` are unchanged.

**Media settings.** `MEDIA_URL = "media/"` and `MEDIA_ROOT = BASE_DIR / "media"`, with working defaults and no `.env` required. Django serves media only when `DEBUG` is on, through the standard `static()` helper in `config/urls.py`. `media/` is gitignored: it is runtime data, like `db.sqlite3`.

**Display.**

- Catalog card: a square box (`aspect-square`) with the image cropped to fill (`object-cover`). Portrait photos lose a little height; landscape placeholders lose a little width.
- Product page: the full image at its natural shape, as today.
- Back-office product list: a small square thumbnail column.
- Back-office edit form: the current image shown above the file input.
- Image `alt` text stays the product name.

**The product form.** `ProductForm` gains `image`. Django's clearable file input provides replace and clear; it is styled with DaisyUI's `file-input` class. `clean_image` rejects uploads over 2 MB; `ImageField` itself rejects files that are not images. The form tag becomes `multipart/form-data`. The limit lives in one named constant.

**Source photos.** `product-images/` is committed and is the seed's source. Each chosen photo is converted once to JPEG, about 1000 pixels wide, keeping its original file name with a `.jpg` extension. The original PNGs stay on disk but out of git (`product-images/*.png` is gitignored). Nothing is resized at runtime.

**The mapping.** Exact matches only: a photo goes to the one product it depicts. It is written out in the seed as `PRODUCT_PHOTOS`, slug to file name:

| Product slug | Source photo |
|---|---|
| `seraphine` | Seraphine GPT Text |
| `hush` | Hush GPT No Text |
| `mindsync` | MindSync GPT 2 |
| `mindsync-duo` | MindSync Duo |
| `recallpro` | RecallPro |
| `moodset` | MoodSet GPT No Text |
| `dreamweaver` | DreamWeaver Matrix GPT 3 |
| `veil` | Veil GPT Text |
| `calm-collar` | Calm Collar GPT Man |
| `syncrest` | SyncRest GPT No Text |
| `soulsear-mark-i` | SoulSear No Text |
| `crowdcalm-array` | CrowdCalm Array No Text |

"SyncRest GPT Text" is not used: the clean photo was chosen over the poster, because the page already prints the name and tagline as text.

**Seed.** `seed` deletes `media/products/` and then saves each mapped photo through the `ImageField`, so it stays destructive and idempotent. A photo missing from `product-images/` is a clear error, not a silent placeholder.

## Testing Decisions

Tests use a tiny image generated in memory and a temporary `MEDIA_ROOT`; they never read `product-images/`, never write to the real `media/`, and never invoke `seed`. A shared fixture in `conftest.py` provides both.

Coverage, in priority order:

1. `Product.image_url`: photo URL when set, category placeholder when not, `default.svg` for an unlisted category.
2. `ProductForm`: accepts a valid image, rejects a non-image, rejects a file over 2 MB, clears an existing photo.
3. Back-office views: create and update with an upload store the file; the list shows a thumbnail for both kinds of product.
4. Storefront: catalog and product page render the photo URL for a product with a photo and the placeholder URL for one without.
5. Seed data: every `PRODUCT_PHOTOS` slug is a product in `CATALOG`, and every file it names exists in `product-images/`.

## Out of Scope

- Thumbnails in the cart, checkout, and order pages. Order pages show past purchases, and a later photo change should not rewrite them.
- More than one photo per product, galleries, zoom.
- Automatic resizing, thumbnail generation, or format conversion of uploads. The 2 MB limit is the only guard.
- Sharing one photo across a product line. Variants without their own photo keep their placeholder.
- Cleaning up replaced or cleared files. Django leaves the old file in `media/`; this is a known limitation, acceptable because `seed` clears `media/products/` on every rebuild.
- Serving media in production (`DEBUG` off).
- Any JavaScript, including a preview of a file chosen but not yet saved.
