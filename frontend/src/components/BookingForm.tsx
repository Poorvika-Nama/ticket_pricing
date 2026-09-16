import { useState } from "react";
import { priceBooking, type BookingPayload } from "../api";
import type { Receipt, SeatTier } from "../types";

type Props = {
  tiers: SeatTier[];
  onReceipt: (receipt: Receipt | null) => void;
};

const FESTIVAL = { flat_amount_paise: 2000 };
const MEMBER = { percentage: 10, cap_paise: 3000 };
const FEE = { per_ticket_fee_paise: 500 };
const TAX = { gst_rate_percent: 18 };

export default function BookingForm({ tiers, onReceipt }: Props) {
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [festival, setFestival] = useState(true);
  const [member, setMember] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function setQuantity(name: string, quantity: number) {
    setQuantities((current) => ({ ...current, [name]: quantity }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    onReceipt(null);
    const selected = Object.fromEntries(
      Object.entries(quantities).filter(([, quantity]) => quantity > 0),
    );
    const payload: BookingPayload = {
      show: { id: "sample-show", seat_tiers: tiers },
      booking_request: { show_id: "sample-show", quantities: selected },
      festival_discount: festival ? FESTIVAL : null,
      member_discount: member ? MEMBER : null,
      fee_config: FEE,
      tax_config: TAX,
    };
    try {
      const receipt = await priceBooking(payload);
      onReceipt(receipt);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to price booking.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card booking-form" onSubmit={submit}>
      <div className="section-heading">
        <div>
          <span className="eyebrow">Sample show</span>
          <h2>Select your seats</h2>
        </div>
        <span className="show-pill">SHOW-01</span>
      </div>

      <div className="tier-list">
        {tiers.map((tier) => {
          const soldOut = tier.available_seats === 0;
          const quantity = quantities[tier.name] || 0;
          return (
            <div className={`tier ${soldOut ? "disabled" : ""}`} key={tier.name}>
              <div className="tier-info">
                <h3>{tier.name}</h3>
                <p>{soldOut ? "Sold out" : `${tier.available_seats} seats remaining`}</p>
              </div>
              <div className="tier-price">₹{(tier.price_paise / 100).toFixed(2)}</div>
              <select
                aria-label={`Quantity for ${tier.name}`}
                value={quantity}
                disabled={soldOut}
                onChange={(event) => setQuantity(tier.name, Number(event.target.value))}
              >
                {Array.from({ length: Math.min(tier.available_seats, 10) + 1 }, (_, index) => (
                  <option value={index} key={index}>{index}</option>
                ))}
              </select>
            </div>
          );
        })}
      </div>

      <div className="discounts">
        <label className="toggle-row">
          <input type="checkbox" checked={festival} onChange={(e) => setFestival(e.target.checked)} />
          <span><strong>Festival discount</strong><small>₹20.00 flat discount</small></span>
        </label>
        <label className="toggle-row">
          <input type="checkbox" checked={member} onChange={(e) => setMember(e.target.checked)} />
          <span><strong>Member discount</strong><small>{MEMBER.percentage}% off, capped at ₹{(MEMBER.cap_paise / 100).toFixed(2)}</small></span>
        </label>
      </div>

      {error && <div className="error" role="alert">{error}</div>}
      {loading && <p className="loading">Calculating your price…</p>}
      <button className="primary" type="submit" disabled={loading || tiers.every((tier) => tier.available_seats === 0)}>
        {loading ? "Getting price…" : "Get price"}
      </button>
    </form>
  );
}
