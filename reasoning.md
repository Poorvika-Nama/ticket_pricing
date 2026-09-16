# Project Reasoning — Cinema Pricing Engine

## 1. Problem Understanding

The project is designed as a cinema ticket pricing engine rather than a simple price calculator.

The main requirement is to take a booking request for a show, determine the ticket cost from the available seat tiers, apply applicable discounts, add convenience fees and GST, and return a transparent itemized bill.

The design was intentionally built in phases so that pricing rules, API concerns, frontend concerns, testing, and future extensions remain separated.

---

## 2. Core Design Decisions

### Separate pricing rules from the API

The actual pricing logic lives in `pricing_engine/engine.py` instead of being implemented inside FastAPI routes.

**Reason:**
- Pricing rules should be reusable outside HTTP requests.
- The business logic can be unit tested independently.
- The API becomes a thin interface over the pricing engine.
- Future interfaces (CLI, another API, batch processing, etc.) can reuse the same engine.

### Use dataclasses for the domain model

The main domain concepts are represented using dataclasses in `pricing_engine/models.py`:

- `SeatTier`
- `Show`
- `BookingRequest`
- `FestivalDiscount`
- `MemberDiscount`
- `FeeConfig`
- `TaxConfig`

**Reason:** These objects describe the data used by the pricing engine without coupling the core model to FastAPI or frontend code.

---

## 3. Pricing Flow

The pricing calculation follows a predictable pipeline:

```text
Booking Request
      ↓
Validate quantities
      ↓
Validate seat tier
      ↓
Validate inventory
      ↓
Calculate base ticket total
      ↓
Apply festival discount
      ↓
Apply member discount
      ↓
Calculate convenience fee
      ↓
Calculate GST on tickets
      ↓
Calculate GST on fee
      ↓
Calculate grand total
      ↓
Return itemized receipt
```

This order is deliberate because changing the order of financial operations can change the final amount.

---

## 4. Inventory and Validation Reasoning

A booking should never silently succeed when its requested quantity is invalid.

The engine therefore validates:

1. Quantity must be positive.
2. Requested seat tier must exist for the show.
3. Requested quantity must not exceed available inventory.

A dedicated `SoldOutError` is used for inventory-related failures.

**Reason:** This keeps business-rule failures explicit and allows the API layer to translate them into an appropriate HTTP response.

---

## 5. Discount Ordering

The discount pipeline applies the festival discount before the membership percentage discount.

```text
Base Total
   ↓
Festival Flat Discount
   ↓
Member Percentage Discount
   ↓
Discounted Ticket Total
```

The member discount is calculated using the remaining ticket amount and is subject to its configured cap.

**Reason:** Discount ordering is a business rule. Applying the percentage before the flat discount would produce a different result, so the order is kept explicit in the engine rather than hidden in the UI.

---

## 6. Money Representation

Prices are represented in **paise as integers** rather than floating-point rupees.

For example:

```text
₹950.00 → 95000 paise
₹20.00  → 2000 paise
```

Decimal arithmetic with `ROUND_HALF_UP` is used where percentage calculations require rounding.

**Reason:** Floating-point arithmetic can introduce precision errors in financial calculations. Integer paise gives exact representation for stored monetary values, while `Decimal` provides controlled arithmetic for percentage calculations.

---

## 7. Tax Reasoning

GST is calculated separately for:

- discounted ticket amount
- convenience fee

The final bill therefore exposes:

```text
Tickets after discounts
+ Convenience fee
+ GST on tickets
+ GST on fee
= Grand total
```

**Reason:** Keeping these components separate makes the calculation auditable and makes the receipt easier to understand.

---

## 8. Itemized Receipt

The engine returns an itemized result rather than only a final number.

The receipt contains values such as:

- base total
- festival discount
- member discount
- total after discounts
- convenience fee
- GST on tickets
- GST on fee
- grand total

**Reason:** A pricing system should be explainable. An itemized receipt makes it possible to understand exactly how the final price was produced and makes testing individual calculation stages easier.

---

## 9. API Architecture

FastAPI is used as the backend HTTP layer.

The API exposes endpoints for:

- health checking
- booking price calculation
- price-list import

The API validates request/response structures using Pydantic models and maps domain errors to HTTP responses.

For example:

```text
SoldOutError → HTTP 409
ValueError   → HTTP 400
```

**Reason:** HTTP-specific behavior belongs at the API boundary rather than inside the core pricing engine.

---

## 10. Frontend Reasoning

The frontend is implemented separately using React, TypeScript, and Vite.

The frontend is responsible for:

- collecting booking inputs
- displaying the calculated receipt
- importing price lists
- presenting import results
- providing navigation between booking and import views

It does **not** duplicate the core pricing algorithm.

**Reason:** Having pricing logic independently implemented in the frontend could create inconsistent prices between the UI and backend. The backend remains the source of truth for calculations.

---

## 11. API Proxy Decision for Development

During development, the Vite frontend uses an `/api` proxy to communicate with the FastAPI backend.

```text
Browser
   ↓
Vite /api
   ↓
FastAPI :8000
```

**Reason:** A relative `/api` path avoids hard-coding `127.0.0.1` into browser requests. This is particularly useful when the application is running inside GitHub Codespaces, where the browser and development container do not share the same `localhost` context.

---

## 12. Testing Strategy

Testing is split into layers:

### Engine tests

Verify individual business rules such as:

- valid calculations
- invalid quantities
- unavailable seat tiers
- inventory limits
- discount behavior
- rounding
- final bill calculations

### API tests

Verify that HTTP requests are correctly translated into engine calls and that errors receive appropriate status codes.

### Integration tests

Verify the complete pricing flow using realistic booking data.

**Reason:** Layered testing helps identify whether a failure is caused by the business logic, API boundary, or integration between components.

---

## 13. Price Import Reasoning

Price-list import is treated as a separate concern from booking calculation.

The import flow is intended to convert external price data into the application's internal pricing representation.

The imported prices can then be surfaced by the frontend rather than embedding every price directly into the booking UI.

**Reason:** Separating price ingestion from calculation makes it easier to replace the source of prices later, such as a CSV file, database, admin system, or external service.

---

## 14. Configuration vs. Logic

Configuration values such as:

- festival discount amount
- member discount percentage
- member discount cap
- convenience fee
- GST rate

are treated as inputs/configuration rather than being hard-coded into the core calculation algorithm.

The frontend may provide sample configuration for the current demonstration, but the calculation itself remains in the backend engine.

**Reason:** Business rules are likely to change. Keeping configuration separate makes the system easier to extend without rewriting the calculation pipeline.

---

## 15. Error Handling Philosophy

Errors are handled explicitly instead of allowing invalid bookings to produce misleading bills.

The system distinguishes between business validation errors and inventory-related errors.

This makes failures understandable to both developers and API consumers.

---

## 16. Repository and Dependency Design

The Python project is packaged as `cinema-pricing-engine` using a `pyproject.toml` configuration.

The package configuration explicitly discovers the `pricing_engine` package so that unrelated top-level directories such as `frontend` do not get treated as Python packages.

Testing dependencies are kept in a separate optional `test` dependency group.

**Reason:** This keeps installation predictable and avoids coupling the Python package structure to the React frontend directory.

---

## 17. CI Reasoning

GitHub Actions runs the Python test suite across supported Python versions.

The project currently targets Python `>=3.11` and tests multiple Python versions.

**Reason:** Testing across supported versions helps catch compatibility problems before changes are merged.

---

## 18. What We Intentionally Avoided

### Pricing logic in React

Avoided because the backend should remain the source of truth.

### Floating-point money calculations

Avoided because financial values need predictable precision.

### Mixing API and business logic

Avoided to keep the engine reusable and testable.

### Silent inventory failures

Avoided because a booking must not exceed available seats.

### Returning only a final total

Avoided because users and developers need to understand how the total was calculated.

### Treating frontend and backend as one application layer

Avoided because they have different responsibilities and can evolve independently.

---

## 19. Example Calculation Reasoning

For a booking whose base ticket total is ₹950:

```text
Base total                 ₹950.00
Festival discount           -₹20.00
Member discount             -₹93.00
                           ---------
After discounts             ₹837.00

Convenience fee              ₹20.00
GST on tickets              ₹150.66
GST on fee                    ₹3.60
                           ---------
Grand total                ₹1,011.26
```

In paise, the corresponding expected result is:

```text
base_total            = 95000
festival_discount     = 2000
member_discount       = 9300
total_after_discounts = 83700
convenience_fee       = 2000
gst_on_tickets        = 15066
gst_on_fee            = 360
grand_total           = 101126
```

This example is useful as a reference for understanding the intended order of operations.

---

## 20. Overall Engineering Approach

The project follows a simple principle:

> **Keep business rules explicit, calculations deterministic, responsibilities separated, and results explainable.**

The architecture is intentionally more structured than a single-file calculator because the project is being developed as a realistic software system that can evolve from a pricing engine into a complete cinema booking service.

The current implementation provides the foundation for future features such as:

- additional discount types
- dynamic pricing
- seat-specific pricing
- database-backed inventory
- authentication
- admin pricing management
- persistent bookings
- production deployment

These future capabilities should be added without moving business logic into the presentation layer or tightly coupling the pricing engine to a specific interface.
