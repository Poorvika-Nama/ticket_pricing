from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from .models import SeatTier


class PriceParseError(ValueError):
    """Raised when a raw seat price cannot be parsed or is negative."""


@dataclass
class ImportReport:
    imported: list[dict[str, int | str]]
    deduplicated: list[dict[str, int | str]]
    rejected: list[dict[str, object]]

    def to_summary_string(self) -> str:
        lines = [
            f"Imported: {len(self.imported)}",
            f"Deduplicated: {len(self.deduplicated)}",
            f"Rejected: {len(self.rejected)}",
        ]
        lines.extend(
            f"Rejected row: {entry['reason']}"
            for entry in self.rejected
        )
        return "\n".join(lines)


def normalize_tier_name(raw_name: str) -> str:
    """Normalize a seat-tier name for consistent matching."""
    if not isinstance(raw_name, str):
        raw_name = str(raw_name)
    return " ".join(raw_name.strip().split()).title()


def parse_price_to_paise(raw_price: object) -> int:
    """Parse a messy non-negative price into integer paise."""
    if raw_price is None or (isinstance(raw_price, str) and not raw_price.strip()):
        raise PriceParseError("blank price")

    value = str(raw_price).strip()
    cleaned = re.sub(r"[₹$€£]|(?i:rs\\.?)", "", value)
    cleaned = cleaned.replace(",", "")
    cleaned = re.sub(r"[A-Za-z]", "", cleaned).strip()

    if not cleaned:
        raise PriceParseError("unparseable price")

    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        raise PriceParseError("unparseable price") from None

    if not amount.is_finite():
        raise PriceParseError("unparseable price")
    if amount < 0:
        raise PriceParseError("negative price")

    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def clean_price_list(raw_rows: list[dict[str, object]]) -> ImportReport:
    """Clean, validate, and de-duplicate raw tier price rows in input order."""
    imported: list[dict[str, int | str]] = []
    deduplicated: list[dict[str, int | str]] = []
    rejected: list[dict[str, object]] = []
    winners: dict[str, int] = {}

    for raw_row in raw_rows:
        raw_name = raw_row.get("tier_name")
        canonical_name = normalize_tier_name(raw_name)

        try:
            price_paise = parse_price_to_paise(raw_row.get("price"))
        except PriceParseError as exc:
            reason = str(exc)
            rejected_reason = (
                "blank price"
                if reason == "blank price"
                else "negative price"
                if reason == "negative price"
                else "unparseable price"
            )
            rejected.append({"raw_row": raw_row, "reason": rejected_reason})
            continue

        if canonical_name in winners:
            winning_price = winners[canonical_name]
            reason = (
                "same price repeated"
                if price_paise == winning_price
                else "duplicate name with conflicting price"
            )
            existing = next(
                item for item in deduplicated
                if item["tier_name"] == canonical_name
                and item["price_paise"] == price_paise
                and item["reason"] == reason
            ) if False else None

            # Keep one report entry per collapsed row while exposing how many
            # duplicate rows were collapsed for this normalized name/price.
            matching = next(
                (
                    item for item in deduplicated
                    if item["tier_name"] == canonical_name
                    and item["price_paise"] == price_paise
                    and item["reason"] == reason
                ),
                None,
            )
            if matching is None:
                deduplicated.append(
                    {
                        "tier_name": canonical_name,
                        "price_paise": price_paise,
                        "duplicate_count": 1,
                        "reason": reason,
                    }
                )
            else:
                matching["duplicate_count"] = int(matching["duplicate_count"]) + 1
            continue

        winners[canonical_name] = price_paise
        imported.append({"tier_name": canonical_name, "price_paise": price_paise})

    return ImportReport(
        imported=imported,
        deduplicated=deduplicated,
        rejected=rejected,
    )


def build_seat_tiers(imported_list: list[dict[str, int | str]]) -> list[SeatTier]:
    """Convert clean imported entries into SeatTier objects."""
    return [
        SeatTier(
            name=str(entry["tier_name"]),
            price_paise=int(entry["price_paise"]),
            available_seats=0,
        )
        for entry in imported_list
    ]
