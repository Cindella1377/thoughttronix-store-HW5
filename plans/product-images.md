# Implementation Plan: The ThoughtTronix Store — Product Photos

*Companion to `prd/product-images.md`. The PRD owns the requirements; this plan owns the sequence. Where a task says "per the PRD," the PRD's wording is authoritative — do not improvise alternatives. The suite must be green at every phase boundary.*

---

## Phase 1 — The Image Field and the Fallback Rule

**Goal:** A product can hold a photo and can always say which image to show — proven entirely by tests, before any page changes.

**Tasks:**
1. `uv add pillow`.
2. `config/settings.py`: `MEDIA_URL` and `MEDIA_ROOT` per the PRD. `config/urls.py`: serve media with the `static()` helper when `DEBUG` is on.
3. `.gitignore`: add `media/`.
4. `Product.image` per the PRD. Migration. Update the "No media handling in the core" comment in `products/models.py`.
5. `Product.image_url` property per the PRD.
6. `conftest.py`: a fixture that points `MEDIA_ROOT` at a temporary directory, and a fixture that returns a tiny in-memory image upload.
7. Model tests — PRD coverage priority 1.

**Verification.** *Automated:* model tests green; Ruff clean; existing suite untouched and green. *Manual:* in the Django admin, upload a photo to one product; in `manage.py shell`, its `image_url` starts with `/media/products/` and another product's ends with its category's `.svg`.

**Out of bounds:** every template, the back-office form, seed.

---

## Phase 2 — Photos on the Storefront

**Goal:** Customers see the photo where there is one and the placeholder where there is not.

**Tasks:**
1. `templates/products/catalog.html`: the card image uses `product.image_url` inside a square box, cropped to fill, per the PRD.
2. `templates/products/detail.html`: the image uses `product.image_url`; shape unchanged.
3. Storefront tests — PRD coverage priority 4.

**Verification.** *Automated:* catalog and product page tests for both kinds of product. *Manual:* with the product from Phase 1's admin upload, the catalog shows its photo in a square card level with its placeholder neighbours; its product page shows the whole photo; a product without a photo looks as it did before.

**Out of bounds:** cart, checkout, and order templates — these never gain images. Back office, seed.

---

## Phase 3 — Photos in the Back Office

**Goal:** Staff upload, replace, and clear photos, and can see which products have one.

**Tasks:**
1. `ProductForm`: add `image`; `clean_image` enforcing the 2 MB limit from a named constant; `file-input` styling for the widget in `StyledModelForm`. Form tests first — PRD coverage priority 2.
2. `templates/products/manage_product_form.html`: `enctype="multipart/form-data"`; show the product's current image above the fields when editing. The create and update views are class-based and already pass uploaded files to the form; confirm with a test, change nothing unless it fails.
3. `templates/products/manage_products.html`: a thumbnail column using `product.image_url`.
4. Back-office view tests — PRD coverage priority 3.

**Verification.** *Automated:* form and view tests green. *Manual:* as `employee`, upload a photo to a product and see it in the list, the edit form, and the catalog; replace it; tick Clear and see the placeholder return; try a `.txt` file and a file over 2 MB and read both error messages.

**Out of bounds:** resizing uploads, deleting old files, seed.

---

## Phase 4 — The Photographs and the Seed

**Goal:** A fresh clone plus `seed` shows twelve real photos and the placeholders beside them.

**Tasks:**
1. Convert the twelve photos named in the PRD's mapping to JPEG, about 1000 pixels wide, written beside the originals in `product-images/` with a `.jpg` extension. A one-off script run from the scratchpad, not committed. Do not modify, move, or delete any PNG.
2. `.gitignore`: add `product-images/*.png`. Commit the twelve JPEGs.
3. `seed`: `PRODUCT_PHOTOS` per the PRD's table; `_clear` deletes `media/products/`; after the catalog is created, save each mapped photo through `Product.image`. A missing source file raises a `CommandError` naming it.
4. Seed data test — PRD coverage priority 5 — reading `PRODUCT_PHOTOS` and `CATALOG` directly, without invoking the command.

**Verification.** *Automated:* seed data test green; full suite green. *Manual:* `seed`, then browse the catalog: twelve photos, the rest placeholders; run `seed` again and confirm `media/products/` holds exactly twelve files; `git status` shows no `media/` and no PNGs.

**Out of bounds:** photos for variants, any change to placeholder artwork.

---

## Phase 5 — Documentation

**Goal:** The project's own records describe the feature.

**Tasks:**
1. `CLAUDE.md`: name this PRD and plan in the opening paragraph; note `media/` and `product-images/` in the project layout; note `Product.image_url` as the one place that chooses photo or placeholder.
2. `PROMPTS.md`: append this session's entries. Never rewrite earlier ones.
3. Final pass: `uv run pytest`, `uv run ruff check .`, `uv run ruff format .`.

**Verification.** *Automated:* suite green, Ruff clean. *Manual:* from a fresh clone, `uv sync`, `migrate`, `seed`, and `tailwind runserver` produce the demo catalog with photos.

**Out of bounds:** anything in the PRD's Out of Scope section.
