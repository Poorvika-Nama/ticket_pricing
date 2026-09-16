import type { Receipt } from "../types";

type Props = { receipt: Receipt };

const labels: Array<[keyof Receipt, string]> = [
  ["base_total", "Base total"],
  ["festival_discount", "Festival discount"],
  ["member_discount", "Member discount"],
  ["total_after_discounts", "Total after discounts"],
  ["convenience_fee", "Convenience fee"],
  ["gst_on_tickets", "GST on tickets"],
  ["gst_on_fee", "GST on fee"],
  ["grand_total", "Grand total"],
];

export default function ReceiptBreakdown({ receipt }: Props) {
  return (
    <section className="card receipt" aria-label="Itemized receipt">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Price breakdown</span>
          <h2>Your receipt</h2>
        </div>
      </div>
      <div className="receipt-lines">
        {labels.map(([key, label]) => (
          <div key={key} className={key === "grand_total" ? "receipt-line total" : "receipt-line"}>
            <span>{label}</span>
            <strong>{receipt[key].rupees}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
