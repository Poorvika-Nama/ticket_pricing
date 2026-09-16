import { useState } from "react";
import BookingForm from "../components/BookingForm";
import ReceiptBreakdown from "../components/ReceiptBreakdown";
import type { Receipt, SeatTier } from "../types";

type Props = { tiers: SeatTier[] };

export default function BookingPage({ tiers }: Props) {
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  return (
    <main className="page">
      <div className="page-intro">
        <div><span className="eyebrow">Cinema checkout</span><h1>Book your seats</h1><p>Choose a show, select seats, and get an itemized price instantly.</p></div>
      </div>
      <div className="booking-layout">
        <BookingForm tiers={tiers} onReceipt={setReceipt} />
        {receipt ? <ReceiptBreakdown receipt={receipt} /> : (
          <aside className="card empty-receipt"><span className="receipt-mark">₹</span><h2>Your receipt</h2><p>Your itemized total will appear here after you request a price.</p></aside>
        )}
      </div>
    </main>
  );
}
