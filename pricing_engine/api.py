from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .engine import SoldOutError, price_booking
from .models import (
    BookingRequest,
    FestivalDiscount,
    FeeConfig,
    MemberDiscount,
    SeatTier,
    Show,
    TaxConfig,
)
from .price_import import ImportReport, clean_price_list


app = FastAPI(title="Cinema Pricing Engine API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SeatTierRequest(BaseModel):
    name: str
    price_paise: int = Field(ge=0)
    available_seats: int = Field(ge=0)


class ShowRequest(BaseModel):
    id: str
    seat_tiers: list[SeatTierRequest]


class BookingRequestModel(BaseModel):
    show_id: str
    quantities: dict[str, int]


class FestivalDiscountRequest(BaseModel):
    flat_amount_paise: int = Field(ge=0)


class MemberDiscountRequest(BaseModel):
    percentage: float = Field(ge=0)
    cap_paise: int = Field(ge=0)


class FeeConfigRequest(BaseModel):
    per_ticket_fee_paise: int = Field(ge=0)


class TaxConfigRequest(BaseModel):
    gst_rate_percent: float = Field(ge=0)


class PriceBookingRequest(BaseModel):
    show: ShowRequest
    booking_request: BookingRequestModel
    festival_discount: FestivalDiscountRequest | None = None
    member_discount: MemberDiscountRequest | None = None
    fee_config: FeeConfigRequest
    tax_config: TaxConfigRequest


class MoneyLineItem(BaseModel):
    paise: int
    rupees: str


class PriceBookingResponse(BaseModel):
    base_total: MoneyLineItem
    festival_discount: MoneyLineItem
    member_discount: MoneyLineItem
    total_after_discounts: MoneyLineItem
    convenience_fee: MoneyLineItem
    gst_on_tickets: MoneyLineItem
    gst_on_fee: MoneyLineItem
    grand_total: MoneyLineItem


class RawPriceRow(BaseModel):
    tier_name: str
    price: Any


class ImportedEntry(BaseModel):
    tier_name: str
    price_paise: int


class DeduplicatedEntry(BaseModel):
    tier_name: str
    price_paise: int
    duplicate_count: int
    reason: str


class RejectedEntry(BaseModel):
    raw_row: dict[str, Any]
    reason: str


class ImportReportResponse(BaseModel):
    imported: list[ImportedEntry]
    deduplicated: list[DeduplicatedEntry]
    rejected: list[RejectedEntry]


def _money_item(paise: int) -> MoneyLineItem:
    return MoneyLineItem(paise=paise, rupees=f"₹{paise / 100:.2f}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/price-booking", response_model=PriceBookingResponse)
def price_booking_endpoint(request: PriceBookingRequest) -> PriceBookingResponse:
    show = Show(
        id=request.show.id,
        seat_tiers=[SeatTier(**tier.model_dump()) for tier in request.show.seat_tiers],
    )
    booking_request = BookingRequest(**request.booking_request.model_dump())
    festival_discount = (
        FestivalDiscount(**request.festival_discount.model_dump())
        if request.festival_discount
        else None
    )
    member_discount = (
        MemberDiscount(**request.member_discount.model_dump())
        if request.member_discount
        else None
    )
    fee_config = FeeConfig(**request.fee_config.model_dump())
    tax_config = TaxConfig(**request.tax_config.model_dump())

    try:
        breakdown = price_booking(
            show,
            booking_request,
            festival_discount,
            member_discount,
            fee_config,
            tax_config,
        )
    except SoldOutError as exc:
        tier_name = exc.args[0] if exc.args else "requested tier"
        raise HTTPException(
            status_code=409,
            detail=f"Not enough seats available for tier '{tier_name}'",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PriceBookingResponse(
        **{key: _money_item(value) for key, value in breakdown.items()}
    )


@app.post("/import-price-list", response_model=ImportReportResponse)
def import_price_list(rows: list[RawPriceRow]) -> ImportReportResponse:
    report: ImportReport = clean_price_list([row.model_dump() for row in rows])
    return ImportReportResponse(
        imported=report.imported,
        deduplicated=report.deduplicated,
        rejected=report.rejected,
    )
