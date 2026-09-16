from dataclasses import dataclass


@dataclass
class SeatTier:
    name: str
    price_paise: int
    available_seats: int


@dataclass
class Show:
    id: str
    seat_tiers: list[SeatTier]


@dataclass
class BookingRequest:
    show_id: str
    quantities: dict[str, int]


@dataclass
class FestivalDiscount:
    flat_amount_paise: int


@dataclass
class MemberDiscount:
    percentage: float
    cap_paise: int


@dataclass
class FeeConfig:
    per_ticket_fee_paise: int


@dataclass
class TaxConfig:
    gst_rate_percent: float
