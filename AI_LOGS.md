Pasted markdown(1).md
File
and forget codespaces just update in repo

Phase 5 is now updated directly in the GitHub repository.

Added edge-case coverage
Exact inventory boundary succeeds.
One over inventory raises SoldOutError.
Member discount cap exactly matching the percentage discount.
Zero-quantity booking raises a clear ValueError.
Free (0 paise) tickets with fee + GST.
0% GST tax-holiday scenario.
Added CI

Created .github/workflows/tests.yml with GitHub Actions that runs pytest on:

Every push to main
Every pull request targeting main
Python 3.11, 3.12, and 3.13

Everything is committed directly to Poorvika-Nama/ticket_pricing; no Codespaces involved.

Add a new module pricing_engine/price_import.py that imports a messy
seat-class price list (given as a list of raw dict rows, e.g. from a CSV
with columns "tier_name" and "price") and produces a clean, de-duplicated
list of SeatTier-ready entries plus a structured import report.

Implement:

1. normalize_tier_name(raw_name) -> canonical name:
   - Trim whitespace, collapse internal whitespace, title-case the result
   - Two names that differ only by case/whitespace normalize to the same
     canonical name

2. parse_price_to_paise(raw_price) -> int (paise), raising a PriceParseError
   for anything invalid:
   - Accept plain numbers ("500", "500.00"), currency-prefixed values
     ("₹500", "Rs. 500", "Rs.500"), and thousands separators ("1,000")
   - Strip currency symbols/letters and separators, parse as Decimal,
     convert to integer paise (round-half-up)
   - Reject blank/whitespace-only values and anything that isn't a valid
     non-negative number after stripping symbols
   - Reject negative prices explicitly, with a distinct error message from
     "unparseable"

3. clean_price_list(raw_rows) -> ImportReport, where raw_rows is a list of
   dicts with "tier_name" and "price" keys, and ImportReport is a dataclass
   with three fields:
   - imported: list of {tier_name, price_paise} — the final clean list,
     one entry per unique normalized name
   - deduplicated: list of {tier_name, price_paise, duplicate_count,
     reason} — entries that were collapsed, reason is either
     "same price repeated" or "duplicate name with conflicting price"
   - rejected: list of {raw_row, reason} — reason is one of "blank price",
     "unparseable price", "negative price"

   Processing rule: process rows in the given order. The first valid
   (parseable, non-negative) price seen for a normalized name is the one
   that wins and goes into imported. Any later row for the same
   normalized name is logged into deduplicated (not imported), with
   the reason depending on whether its price matches the winning price.
   Rows with unparseable/blank/negative prices always go to rejected,
   even if their name duplicates another row.

Add a method to ImportReport, to_summary_string(), that renders a short
human-readable report: counts of imported/deduplicated/rejected, followed
by one line per rejected row with its reason.

Add unit tests in tests/test_price_import.py covering:
- Same tier name in different cases and whitespace, same price -> deduped
- Same tier name, different valid prices -> first wins, second rejected as
  conflicting duplicate
- Prices in each accepted format (plain, currency-prefixed, thousands sep)
- Blank price, non-numeric price, negative price -> each rejected with the
  correct reason
- A realistic messy batch (mix of all the above) producing the correct
  imported/deduplicated/rejected counts

Do not change pricing_engine/engine.py in this phase — just wire
clean_price_list's imported output into a list of SeatTier objects at
the end, as a small helper function build_seat_tiers(imported_list) that
callers can pass into Show.

Implemented directly in Poorvika-Nama/ticket_pricing on main.

Added
pricing_engine/price_import.py
normalize_tier_name()
parse_price_to_paise()
PriceParseError
ImportReport
clean_price_list()
build_seat_tiers()
Decimal + ROUND_HALF_UP price handling
Duplicate tracking and structured rejection reasons
Human-readable to_summary_string()
tests/test_price_import.py
Case/whitespace normalization
Same-price deduplication
Conflicting duplicate handling
All requested price formats
Blank/unparseable/negative prices
Rounding behavior
Realistic messy batch
Conversion to SeatTier
Summary reporting

pricing_engine/engine.py was not changed in this phase.

The changes are committed to the repository.

That means the FastAPI backend isn't running yet. 127.0.0.1:8000 only works after you start the server.

From your ticket_pricing repository folder, do this:

1. Open Terminal / PowerShell

Make sure you're inside the project:

cd path\to\ticket_pricing

For example, if it's on your Desktop:

cd Desktop\ticket_pricing
2. Install the backend
pip install -e ".[test]"

If pip doesn't work, try:

python -m pip install -e ".[test]"
3. Start FastAPI
uvicorn pricing_engine.api:app --reload

If uvicorn isn't recognized:

python -m uvicorn pricing_engine.api:app --reload

You should see something similar to:

INFO:     Uvicorn running on http://127.0.0.1:8000

Keep this terminal open.

4. Test it

Now open:

FastAPI Dashboard / Docs

or:

Health Check

The health page should show:

{"status":"ok"}
5. Then start the React dashboard

Open a second terminal:

cd path\to\ticket_pricing\frontend
npm install
npm run dev

Then open the URL Vite gives you, normally:

http://localhost:5173
If step 3 gives an error

Don't guess or change files yet. Copy-paste the entire output from:

python -m uvicorn pricing_engine.api:app --reload

here, and I'll tell you exactly what is wrong.

Perfect. The backend installation issue is fixed, and pip install -e ".[test]" completed successfully.

Your next step is to start both services correctly inside the Codespace.

it still says failed to fetch

Got it. Your backend is definitely starting correctly. The remaining issue is the Codespace → browser connection.

I’ve updated the Vite configuration in your GitHub repository so the frontend listens on 0.0.0.0 and proxies API requests to FastAPI.

Now do this exactly in your Codespace.

1. Stop both old servers

In each terminal press:

Ctrl + C
2. Get my latest fix

In the Codespace terminal:

cd /workspaces/ticket_pricing
git pull

You should see the Vite config update.

3. Start FastAPI

Terminal 1:

cd /workspaces/ticket_pricing
python -m uvicorn pricing_engine.api:app --host 0.0.0.0 --port 8000 --reload

Leave this running.

4. Start React

Open a new Codespace terminal:

cd /workspaces/ticket_pricing/frontend
npm install
npm run dev -- --host 0.0.0.0
5. Check PORTS

At the bottom of VS Code/Codespaces, click:

PORTS

You should have:

5173   Forwarded
8000   Forwarded

If they aren't there, click Add Port and add:

5173

and:

8000

For 5173, click the globe/open-browser icon and open the dashboard.

6. Important: don't use the old browser tab

Close the old dashboard tab that was showing:

Failed to fetch

Open the new forwarded 5173 URL from the PORTS tab.

Test the backend separately

Before testing the dashboard, open the forwarded URL for port 8000, not 127.0.0.1.

You should get the API response for:

/health

So if Codespaces gives you something like:

https://xxxxx-8000.app.github.dev

open:

https://xxxxx-8000.app.github.dev/health

It should show:

{"status":"ok"}

If that works, then open the port 5173 URL.

If it STILL says "Failed to fetch"

Don't change anything else yet.

Send me just these two things:

What you see under PORTS (especially the 5173 and 8000 rows)
The exact error from browser F12 → Console

Then I can fix the remaining networking issue directly in the repo.

reasoning.md(thought process)
help me create this file in this project in this it will tell us about what is the thought process we have used for this project

Created reasoning.md directly in your GitHub repository.

Open reasoning.md on GitHub

It documents the thought process and engineering decisions behind the project, including:

Problem understanding
Pricing calculation flow
Why we used dataclasses
Why money is stored in paise
Discount ordering
GST calculation
Inventory validation
API/backend separation
React frontend architecture
Vite proxy decision for Codespaces
Testing strategy
Price import design
Configuration vs. business logic
Error handling
CI/CD reasoning
What we intentionally avoided
Example calculation
Future extensibility

I also kept it focused on why we designed the project this way, rather than simply documenting what each file contains.

Crreate to plan to make this project end to end ticket pricing  give step by step prompts to make this in codespace github by using chatgpt github plugin .

Friday night at the multiplex
The multiplex booking counter keeps mis-pricing tickets and the queue is getting angry. Seats come in tiers — Silver, Gold, Recliner — at different prices, and by showtime some tiers sell out and shouldn’t be bookable. There are offers on: a flat festival discount and a percentage off for members (capped). Every booking then adds a small per-ticket convenience fee and GST on top, and it all has to total to the exact paisa. Customers keep demanding a clear line-by-line breakup of the bill.
Build a pricing engine the counter can trust.
(The messy real-world money rules are the point — handle each correctly, and build it for any cinema counter, not one show. Get a plain booking total right first, then layer on the offers, the fee and the tax.)

Locking the business rules first

Before any prompts, the ambiguous parts of this brief need explicit decisions — otherwise every implementer (or every ChatGPT prompt) will guess differently. Here's the interpretation I'd lock in for Phase 0, which you can adjust:

Money type: everything computed in integer paise internally, only converted to ₹ for display. No floats anywhere in the pricing math.
Discount order: festival flat discount is a per-booking amount, applied to the base total first. Member % discount (capped) is applied to the remainder after the flat discount, then capped.
Fee base: convenience fee is per-ticket, flat, applied after discounts (not discounted itself).
Tax base: GST is charged as two separate line items — GST on the (discounted) ticket amount, and GST on the convenience fee — since these are typically taxed as distinct services. Rates are config, not hardcoded.
Rounding: round each line item to the nearest paisa (round-half-up), then reconcile any residual paisa into the final total line so the grand total always matches the sum of displayed lines exactly.
Sellout: inventory is tracked per tier per show; a booking request is rejected atomically if any tier in the cart doesn't have enough remaining seats.

Everything below assumes these rules — flag any you'd want changed and I'll adjust the phases.

Calculation pipeline
The plan: six phases, each with an approval gate

Each phase below is scoped to be small enough to review as a single diff, with its own ChatGPT prompt block you paste into the GitHub Codespace. Don't run Phase N+1's prompt until you've reviewed and committed Phase N's output.

Phase 0 — Repo scaffold, no pricing logic yet

Goal: empty but structured Python project — module layout, no business logic.

Setup steps (you do these, not ChatGPT):

Create a new GitHub repo, e.g. cinema-pricing-engine.
Open it in a Codespace (Code → Codespaces → Create codespace on main).
In the Codespace, install/enable the ChatGPT GitHub connector (Extensions or the ChatGPT panel, depending on which plugin you're using) and point it at this repo.

Prompt to paste:

Scaffold a Python project called cinema-pricing-engine for a ticket pricing
engine. Create this structure only — no pricing logic yet:

pricing_engine/
  __init__.py
  models.py       # empty, will hold dataclasses later
  engine.py       # empty, will hold the calculator later
tests/
  __init__.py
pyproject.toml     # basic, using pytest as the only dependency
README.md          # one paragraph describing the project's purpose
.gitignore          # standard Python

Do not implement any pricing calculations yet. Just the skeleton, so we can
build it up phase by phase.

Gate: commit this before moving on.

Phase 1 — Domain model + plain base total

Goal: entities (SeatTier, Show, Inventory, Booking) and the base total calculation only — no discounts, fee, or tax yet. This nails "get a plain booking total right first."

Prompt to paste:

In pricing_engine/models.py, add dataclasses for a generic cinema pricing
domain:
- SeatTier: name (e.g. Silver/Gold/Recliner), price_paise (int), 
  available_seats (int)
- Show: id, list of SeatTier
- BookingRequest: show_id, dict of {tier_name: quantity}

All money values must be integers in paise — no floats anywhere.

In pricing_engine/engine.py, implement a PricingEngine class with a method
calculate_base_total(show, booking_request) that:
1. Validates every requested tier exists on the show
2. Validates available_seats >= requested quantity for every tier
   (raise a SoldOutError with the offending tier name if not)
3. Returns the base total in paise as sum(tier.price_paise * qty)

Add unit tests in tests/test_engine.py covering: normal multi-tier booking,
a tier that's sold out, and a tier requested but not offered on that show.

Do not implement discounts, fees, or tax yet — this phase is base total only.

Gate: review the sellout/error handling, commit.

Phase 2 — Offers layer (flat festival + capped % member)

Goal: discount logic on top of the base total, with the stacking order locked.

Prompt to paste:

Extend pricing_engine/models.py with:
- FestivalDiscount: flat_amount_paise (int)
- MemberDiscount: percentage (float, e.g. 10.0 for 10%), cap_paise (int)

Extend pricing_engine/engine.py's PricingEngine with a method
apply_discounts(base_total_paise, festival_discount=None, member_discount=None)
that:
1. Subtracts the flat festival discount from the base total first
   (never below zero — clamp at zero if the discount exceeds the total)
2. Then applies the member percentage discount to the remainder, capped at
   cap_paise (i.e. the percentage discount amount is min(pct * remainder, cap))
3. Returns a breakdown: {base_total, festival_discount_applied,
   member_discount_applied, total_after_discounts} all in paise

Add unit tests: no discounts, only festival, only member, both stacked,
festival discount exceeding total, member discount hitting its cap.

Gate: confirm the stacking order matches intent, commit.

Phase 3 — Convenience fee + GST + exact paisa reconciliation

Goal: the trickiest part — fee, tax on two separate bases, and rounding that guarantees the line items sum to the displayed total exactly.

Prompt to paste:

Extend pricing_engine/models.py with:
- FeeConfig: per_ticket_fee_paise (int)
- TaxConfig: gst_rate_percent (float) — same rate applies to both the
  ticket amount and the fee amount, but as separate line items

Extend PricingEngine with calculate_final_bill(...) that takes the output
of apply_discounts, ticket_count, FeeConfig, and TaxConfig, and:
1. Computes convenience_fee_paise = per_ticket_fee_paise * ticket_count
2. Computes gst_on_tickets_paise = round(total_after_discounts * gst_rate/100)
   using round-half-up on paise (no floats in the final arithmetic — use
   Decimal or integer math, not float multiplication)
3. Computes gst_on_fee_paise = round(convenience_fee_paise * gst_rate/100)
   with the same rounding rule
4. Sums every line item to grand_total_paise
5. Returns a full breakdown object listing every line: base_total,
   festival_discount, member_discount, total_after_discounts,
   convenience_fee, gst_on_tickets, gst_on_fee, grand_total
6. Asserts (in a test, not in production code) that summing the returned
   line items always exactly equals grand_total_paise — no rounding drift

Add unit tests: a case where rounding would naively drift by a paisa, a
zero-discount booking, a heavily discounted booking, and a large multi-tier
booking. Also add a test that renders the breakdown as a human-readable
receipt string, one line per item, ending in the total.

Gate: this is the phase to scrutinize hardest — check the rounding test actually exercises a drift-prone case (e.g. an odd rupee amount at a rate like 18%). Commit only after you're satisfied.

Phase 4 — Public API + config-driven reuse (not hardcoded to one show)

Goal: make it usable by "any cinema counter," not one hardcoded show — configs for tiers, offers, fee, and tax are all inputs, not constants.

Prompt to paste:

Add a single public entry point, price_booking(show, booking_request,
festival_discount, member_discount, fee_config, tax_config) in engine.py
that chains calculate_base_total -> apply_discounts -> calculate_final_bill
and returns the full itemized breakdown.

Make sure nothing in pricing_engine hardcodes a specific show, cinema, tier
name, discount value, fee amount, or GST rate — all of that must come in
through the function arguments or config objects, so the same engine works
for any cinema counter's configuration.

Add an example script in examples/sample_booking.py that builds a sample
Show with Silver/Gold/Recliner tiers, a festival discount, a member
discount, a fee config, and a tax config, calls price_booking, and prints
the itemized receipt.

Add integration tests in tests/test_integration.py that run a few full
end-to-end bookings through price_booking and check the printed receipt
lines match the expected breakdown.

Gate: run the example script yourself in the Codespace terminal, sanity-check the receipt reads clearly, commit.

Phase 5 — Edge-case hardening + CI

Goal: the ugly cases customers/QA will actually hit, plus a GitHub Actions check so future changes can't silently break the paisa-exactness guarantee.

Prompt to paste:

Add edge-case tests to the existing test suite for:
- Booking exactly at remaining inventory (boundary, should succeed)
- Booking one more than remaining inventory (should raise SoldOutError)
- Member discount cap exactly equal to the computed percentage amount
- Zero-quantity booking request (should raise a clear validation error)
- A tier price of 0 (free seats/comps) combined with fee and GST
- A GST rate of 0 (tax holiday scenario)

Then add .github/workflows/tests.yml that runs pytest on every push and
pull request against main, using Python 3.11+.

Gate: confirm CI goes green on a push, then this is a done, trustworthy v1.

How this plays out in Codespaces day-to-day
Open the Codespace → paste the phase's prompt into the ChatGPT GitHub plugin panel.
Let it propose the diff/PR.
Review the diff in the Codespace's source control view before merging — especially the rounding logic in Phase 3.
Run pytest in the integrated terminal to confirm green before moving to the next phase's prompt.
Commit, then move to the next prompt.

If you want, I can also turn any single phase into a more detailed sub-spec (e.g. spell out the exact rounding algorithm in prose before you hand it to ChatGPT) — useful mainly for Phase 3 since that's where money bugs actually hide.

give me the plan not for gpt but to code with the help of ai platforms

Planning a general AI-assisted project build strategy.
Same six-phase plan — platform-agnostic version

The phases and prompts stay identical (the domain logic doesn't care which AI tool writes it). What changes is the workflow around them, so it works whether you're using Claude Code, Cursor, GitHub Copilot, Windsurf, or ChatGPT — any AI coding assistant that can read your repo and propose diffs.

General workflow, regardless of tool
Set up the repo first, yourself — create it on GitHub, clone it locally or open it in whatever environment your AI tool works in (a Codespace, a local IDE with Copilot/Cursor, or Claude Code in the terminal).
One phase, one prompt, one PR/commit. Never ask the AI tool to "build the whole pricing engine" in one shot — money logic hides bugs in exactly the seams between phases (discount order, rounding, tax base), and a single giant diff makes those seams impossible to review.
You review every diff before merging — especially Phase 3 (fee + GST + rounding). No AI tool gets a pass on that one; read the actual arithmetic.
Run the tests yourself after each phase (pytest locally), not just trust the tool's claim that they pass.
Only proceed to the next phase's prompt after the current one is committed and green.

This discipline matters more than which tool you use — a good prompt fed to a weak model with strict review beats a great model given a vague, unscoped prompt.

Phase 0 — Repo scaffold
Scaffold a Python project called cinema-pricing-engine for a ticket pricing
engine. Create this structure only — no pricing logic yet:

pricing_engine/
  __init__.py
  models.py       # empty, will hold dataclasses later
  engine.py       # empty, will hold the calculator later
tests/
  __init__.py
pyproject.toml     # basic, using pytest as the only dependency
README.md          # one paragraph describing the project's purpose
.gitignore          # standard Python

Do not implement any pricing calculations yet. Just the skeleton, so we can
build it up phase by phase.
Phase 1 — Domain model + plain base total
In pricing_engine/models.py, add dataclasses for a generic cinema pricing
domain:
- SeatTier: name (e.g. Silver/Gold/Recliner), price_paise (int), 
  available_seats (int)
- Show: id, list of SeatTier
- BookingRequest: show_id, dict of {tier_name: quantity}

All money values must be integers in paise — no floats anywhere.

In pricing_engine/engine.py, implement a PricingEngine class with a method
calculate_base_total(show, booking_request) that:
1. Validates every requested tier exists on the show
2. Validates available_seats >= requested quantity for every tier
   (raise a SoldOutError with the offending tier name if not)
3. Returns the base total in paise as sum(tier.price_paise * qty)

Add unit tests in tests/test_engine.py covering: normal multi-tier booking,
a tier that's sold out, and a tier requested but not offered on that show.

Do not implement discounts, fees, or tax yet — this phase is base total only.
Phase 2 — Offers layer
Extend pricing_engine/models.py with:
- FestivalDiscount: flat_amount_paise (int)
- MemberDiscount: percentage (float, e.g. 10.0 for 10%), cap_paise (int)

Extend pricing_engine/engine.py's PricingEngine with a method
apply_discounts(base_total_paise, festival_discount=None, member_discount=None)
that:
1. Subtracts the flat festival discount from the base total first
   (never below zero — clamp at zero if the discount exceeds the total)
2. Then applies the member percentage discount to the remainder, capped at
   cap_paise (i.e. the percentage discount amount is min(pct * remainder, cap))
3. Returns a breakdown: {base_total, festival_discount_applied,
   member_discount_applied, total_after_discounts} all in paise

Add unit tests: no discounts, only festival, only member, both stacked,
festival discount exceeding total, member discount hitting its cap.
Phase 3 — Fee + GST + exact paisa reconciliation (review this one hardest)
Extend pricing_engine/models.py with:
- FeeConfig: per_ticket_fee_paise (int)
- TaxConfig: gst_rate_percent (float) — same rate applies to both the
  ticket amount and the fee amount, but as separate line items

Extend PricingEngine with calculate_final_bill(...) that takes the output
of apply_discounts, ticket_count, FeeConfig, and TaxConfig, and:
1. Computes convenience_fee_paise = per_ticket_fee_paise * ticket_count
2. Computes gst_on_tickets_paise = round(total_after_discounts * gst_rate/100)
   using round-half-up on paise (no floats in the final arithmetic — use
   Decimal or integer math, not float multiplication)
3. Computes gst_on_fee_paise = round(convenience_fee_paise * gst_rate/100)
   with the same rounding rule
4. Sums every line item to grand_total_paise
5. Returns a full breakdown object listing every line: base_total,
   festival_discount, member_discount, total_after_discounts,
   convenience_fee, gst_on_tickets, gst_on_fee, grand_total
6. Asserts (in a test, not in production code) that summing the returned
   line items always exactly equals grand_total_paise — no rounding drift

Add unit tests: a case where rounding would naively drift by a paisa, a
zero-discount booking, a heavily discounted booking, and a large multi-tier
booking. Also add a test that renders the breakdown as a human-readable
receipt string, one line per item, ending in the total.
Phase 4 — Public API, config-driven for any cinema counter
Add a single public entry point, price_booking(show, booking_request,
festival_discount, member_discount, fee_config, tax_config) in engine.py
that chains calculate_base_total -> apply_discounts -> calculate_final_bill
and returns the full itemized breakdown.

Make sure nothing in pricing_engine hardcodes a specific show, cinema, tier
name, discount value, fee amount, or GST rate — all of that must come in
through the function arguments or config objects, so the same engine works
for any cinema counter's configuration.

Add an example script in examples/sample_booking.py that builds a sample
Show with Silver/Gold/Recliner tiers, a festival discount, a member
discount, a fee config, and a tax config, calls price_booking, and prints
the itemized receipt.

Add integration tests in tests/test_integration.py that run a few full
end-to-end bookings through price_booking and check the printed receipt
lines match the expected breakdown.
Phase 5 — Edge cases + CI
Add edge-case tests to the existing test suite for:
- Booking exactly at remaining inventory (boundary, should succeed)
- Booking one more than remaining inventory (should raise SoldOutError)
- Member discount cap exactly equal to the computed percentage amount
- Zero-quantity booking request (should raise a clear validation error)
- A tier price of 0 (free seats/comps) combined with fee and GST
- A GST rate of 0 (tax holiday scenario)

Then add .github/workflows/tests.yml that runs pytest on every push and
pull request against main, using Python 3.11+.
Choosing an AI platform for this
Claude Code (terminal/desktop) or Cursor: good for this repo-scale, multi-file workflow — they read your existing files before writing, so later phases correctly extend Phase 1's dataclasses instead of guessing.
GitHub Copilot Chat: fine phase-by-phase in VS Code, but keep prompts scoped the same way — don't let it "helpfully" implement later phases early.
ChatGPT with repo/GitHub access: works the same as the prompts I gave earlier — those apply here unchanged.

Whichever you pick, the phase boundaries and the Phase 3 review discipline are what actually keep the pricing exact — not the tool.

now there is a twist added in this project which i need to implement in the project too 
so create prompt for the below twist too to give it to chatgpt
The Twist
Your solution must also import a messy seat-class price list — with duplicate names (in different cases), prices in inconsistent formats, blank values, and negative prices. Clean it into a correct price list and report what was imported, de-duplicated, and rejected.

also i need a frontend for this project to run.should allign to the project requirement not too simple

Locking the twist's ambiguous rules first

Same discipline as before — the cleaning rules need explicit decisions before any prompt, since "clean it correctly" hides several judgment calls:

Name normalization: trim whitespace, collapse internal spaces, compare case-insensitively (" gold ", "Gold", "GOLD" are the same tier). Store the canonical form as Title Case.
Duplicate resolution: if the same normalized name appears more than once with the same parsed price → keep one, log the rest as deduplicated. If it appears with different prices → conflict; keep the first valid occurrence in file order, reject the later ones with reason "duplicate name with conflicting price".
Price parsing accepts: plain numbers ("500", "500.00"), currency-prefixed ("₹500", "Rs. 500", "Rs.500"), thousands separators ("1,000"), and surrounding whitespace. Parse to Decimal, convert to integer paise.
Rejected rows: blank/whitespace-only price, unparseable text, and negative prices — each logged with the raw row and a specific reason.
Output: the cleaned list becomes the SeatTier price data your Phase 1 engine already consumes — so this import step sits upstream of the pricing engine, not inside it.

This continues your existing phase numbering — pick up after Phase 5.

Phase 6 — Messy price list import and cleaning

Prompt to paste:

Add a new module pricing_engine/price_import.py that imports a messy
seat-class price list (given as a list of raw dict rows, e.g. from a CSV
with columns "tier_name" and "price") and produces a clean, de-duplicated
list of SeatTier-ready entries plus a structured import report.

Implement:

1. normalize_tier_name(raw_name) -> canonical name:
   - Trim whitespace, collapse internal whitespace, title-case the result
   - Two names that differ only by case/whitespace normalize to the same
     canonical name

2. parse_price_to_paise(raw_price) -> int (paise), raising a PriceParseError
   for anything invalid:
   - Accept plain numbers ("500", "500.00"), currency-prefixed values
     ("₹500", "Rs. 500", "Rs.500"), and thousands separators ("1,000")
   - Strip currency symbols/letters and separators, parse as Decimal,
     convert to integer paise (round-half-up)
   - Reject blank/whitespace-only values and anything that isn't a valid
     non-negative number after stripping symbols
   - Reject negative prices explicitly, with a distinct error message from
     "unparseable"

3. clean_price_list(raw_rows) -> ImportReport, where raw_rows is a list of
   dicts with "tier_name" and "price" keys, and ImportReport is a dataclass
   with three fields:
   - imported: list of {tier_name, price_paise} — the final clean list,
     one entry per unique normalized name
   - deduplicated: list of {tier_name, price_paise, duplicate_count,
     reason} — entries that were collapsed, reason is either
     "same price repeated" or "duplicate name with conflicting price"
   - rejected: list of {raw_row, reason} — reason is one of "blank price",
     "unparseable price", "negative price"

   Processing rule: process rows in the given order. The first valid
   (parseable, non-negative) price seen for a normalized name is the one
   that wins and goes into `imported`. Any later row for the same
   normalized name is logged into `deduplicated` (not `imported`), with
   the reason depending on whether its price matches the winning price.
   Rows with unparseable/blank/negative prices always go to `rejected`,
   even if their name duplicates another row.

Add a method to ImportReport, to_summary_string(), that renders a short
human-readable report: counts of imported/deduplicated/rejected, followed
by one line per rejected row with its reason.

Add unit tests in tests/test_price_import.py covering:
- Same tier name in different cases and whitespace, same price -> deduped
- Same tier name, different valid prices -> first wins, second rejected as
  conflicting duplicate
- Prices in each accepted format (plain, currency-prefixed, thousands sep)
- Blank price, non-numeric price, negative price -> each rejected with the
  correct reason
- A realistic messy batch (mix of all the above) producing the correct
  imported/deduplicated/rejected counts

Do not change pricing_engine/engine.py in this phase — just wire
clean_price_list's `imported` output into a list of SeatTier objects at
the end, as a small helper function build_seat_tiers(imported_list) that
callers can pass into Show.

Gate: check the conflicting-duplicate test case carefully — that's the one rule most likely to be interpreted differently than intended. Commit once satisfied.

Phase 7 — API layer (needed before the frontend has anything to call)

Prompt to paste:

Add a FastAPI app in pricing_engine/api.py exposing:

POST /price-booking
  Body: show config (tiers with names/prices/available_seats), booking
  request (tier -> quantity), festival discount, member discount, fee
  config, tax config — all as JSON matching the existing dataclasses.
  Calls price_booking() from engine.py and returns the full itemized
  breakdown as JSON (every line item in both paise and formatted rupees).

POST /import-price-list
  Body: list of raw rows ({tier_name, price} pairs), e.g. parsed
  client-side from an uploaded CSV.
  Calls clean_price_list() from price_import.py and returns the
  ImportReport as JSON (imported, deduplicated, rejected — all three
  lists, not just the summary string).

GET /health
  Trivial liveness check.

Use Pydantic models for request/response validation that mirror the
existing dataclasses (don't duplicate business logic — the endpoints
should be thin wrappers calling into pricing_engine.engine and
pricing_engine.price_import).

Enable CORS for local development (allow all origins) so a frontend
running on a different port can call this API.

Add pytest-based API tests in tests/test_api.py using FastAPI's TestClient,
covering: a successful booking request, a sold-out tier returning a 4xx
with a clear error message, and an import request with a mixed
clean/messy batch returning the correct report.

Update pyproject.toml to add fastapi, uvicorn, and pydantic as
dependencies, and add a note to README.md on how to run the API locally
with uvicorn.

Gate: run the API locally, hit /health and /price-booking with a sample payload before moving on.

Phase 8 — Frontend

Since the requirement is explicitly "not too simple" and should reflect the project's actual complexity (multi-tier booking, stacked offers, itemized tax breakdown, sellout state, and a separate data-cleaning workflow), the frontend needs at least two real screens rather than a single form. A React app calling the Phase 7 API fits that — plain enough to build in one AI-assisted pass, substantial enough to actually demonstrate the engine's behavior.

Prompt to paste:

Create a React frontend (Vite + TypeScript) in a new frontend/ directory
that talks to the FastAPI backend from Phase 7. Build two screens with
client-side routing:

1. Booking screen (default route "/"):
   - Shows the seat tiers for a selected show, each with live remaining
     inventory; tiers with 0 remaining are visibly disabled, not just
     hidden
   - Quantity selector per tier
   - Toggle for festival discount and member discount (with the member
     discount showing its percentage and cap)
   - A "Get price" button that calls POST /price-booking and renders the
     full itemized receipt: base total, festival discount, member
     discount, total after discounts, convenience fee, GST on tickets,
     GST on fee, grand total — each as its own line, in rupees, with the
     grand total visually emphasized
   - If the booking is rejected for a sold-out tier, show a clear inline
     error naming the tier, not a raw error dump

2. Price import screen (route "/import"):
   - A file upload control accepting a CSV of raw tier_name/price rows
     (parse the CSV client-side into JSON rows)
   - A "Clean and import" button that calls POST /import-price-list
   - Renders the ImportReport as three distinct sections: Imported (table
     of tier name + price), Deduplicated (table of tier name + price +
     duplicate count + reason), Rejected (table of raw row + reason) —
     each section showing its count in the heading
   - The imported tiers from this screen should be usable to populate the
     tier list on the booking screen (via shared state or a simple
     fetch-on-load from a small in-memory store on the backend — your
     choice, but state it in a comment)

Shared requirements:
- A persistent nav between the two screens
- Loading and error states for every API call (no silent failures)
- All money values formatted as rupees with 2 decimal places, computed
  from the paise values returned by the API — never re-do money math in
  the frontend
- Reasonably organized components (not one giant file) — split into at
  least BookingForm, ReceiptBreakdown, PriceImportForm, ImportReport
  components

Add a README section explaining how to run the frontend (npm install,
npm run dev) alongside the backend (uvicorn), including the expected
API base URL as an environment variable.

Do not implement any pricing or cleaning logic in the frontend — it only
calls the two API endpoints and renders their responses.

Gate: run both backend and frontend locally, book a multi-tier order with both offers active, and separately upload a deliberately messy CSV — confirm the receipt totals foot exactly and the import report buckets rows the way you'd expect before calling this done.
