# Handoff: Product Photos — ready to implement

*Written 2026-10-04 at the end of a design session. The next session implements the agreed design.*

## Where things stand

The design for product photos is finished and written down. **No code has been written.** Start at Phase 1 of the plan.

Read these first, in this order:

1. `CLAUDE.md` — project conventions (they override defaults).
2. `prd/product-images.md` — what to build and every decision behind it. Authoritative.
3. `plans/product-images.md` — the five phases, each with tasks, verification, and an "out of bounds" list.

Do not re-open decisions recorded in the PRD. The user chose each one explicitly in a `/grill-me` interview.

## Uncommitted work in the tree

Nothing from this session is committed. `main` was clean at the start; the tree now holds:

- `prd/product-images.md` (new)
- `plans/product-images.md` (new)
- `.claude/skills/handoff/SKILL.md` (new; the user wrote its content)
- `HANDOFF.md` (this file)
- `product-images/` (untracked before this session; 13 PNGs, see below)

The user has not asked for a commit. Ask before committing, and branch off `main` first.

## One thing still open

The PRD and plan were written and summarised to the user, who moved straight to this handoff without saying whether they had read them. Before starting Phase 1, confirm in one line that the two documents match what they meant. In particular, three details went slightly beyond their literal answers:

- Original PNGs stay in `product-images/` and are kept out of git by a `product-images/*.png` ignore rule. Nothing is moved or overwritten.
- The JPEG copies keep the original file names with a `.jpg` extension; the seed maps slug to file name explicitly.
- The photo-or-placeholder choice lives in a single `Product.image_url` property.

## Facts found while exploring (not in the PRD or plan)

- `product-images/` holds 13 PNGs, each 1.7–2.5 MB, about 1122×1402 (portrait 4:5). Twelve are used; `SyncRest GPT Text.png` is deliberately unused.
- Placeholder SVGs in `assets/images/placeholders/` are 400×300 (landscape 4:3), which is why the catalog card needs a fixed square box.
- Today only `templates/products/catalog.html:64` and `templates/products/detail.html:17` render an image, both via `product.category.placeholder_image`.
- `ProductForm` is at `products/forms.py:37`, built on `StyledModelForm` (`products/forms.py:16`), which loops over fields to apply classes; the file input will need its own class there.
- `templates/products/manage_product_form.html` renders every field through `templates/products/partials/_field.html`, and its `<form>` tag has no `enctype` yet.
- The seed's catalog data is a `CATALOG` dict of tuples in `products/management/commands/seed.py`; products are created in `_create_catalog` with `slug=slugify(name)`. The slugs in the PRD's mapping table were derived from the names by hand, not by running `slugify`; the Phase 4 seed-data test will catch any mismatch.
- Pillow is not installed, and settings have no `MEDIA_*` entries.

## Working with this user

- They asked to be treated as a beginner. Explain what a step does and why in plain terms, and say what you are about to change before changing it.
- This is coursework (CIDM 3312, Homework 5). The assignment wording was never shared; if a requirement seems to hinge on it, ask.
- `PROMPTS.md` is the AI-usage log and must be appended to, never rewritten (plan Phase 5). This session's prompts to log, in order: a `/grill-me` request to add catalog product photos with real images plus a baseline placeholder from `product-images/`; eleven one-line answers choosing an option at each interview question (all recorded as decisions in the PRD); a request to create the handoff skill file; and this `/handoff` invocation. Match the existing entry format in `PROMPTS.md`.

## Suggested skills

- `run` — launch the app to do each phase's manual verification in the real storefront and back office.
- `code-review` — review the diff at each phase boundary before moving on.
- `simplify` — a quality pass once Phase 4 is done, before the documentation phase.
- `grill-me` — only if a new design question comes up that the PRD does not answer.
