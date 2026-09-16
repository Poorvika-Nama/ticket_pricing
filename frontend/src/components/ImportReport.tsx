import type { ImportReportData } from "../types";

const money = (paise: number) => `₹${(paise / 100).toFixed(2)}`;

type Props = { report: ImportReportData };

export default function ImportReport({ report }: Props) {
  return (
    <div className="report-grid">
      <section className="card report-section">
        <div className="section-heading"><h2>Imported <span className="count">{report.imported.length}</span></h2></div>
        {report.imported.length === 0 ? <p className="muted">No rows imported.</p> : (
          <div className="table-wrap"><table><thead><tr><th>Tier name</th><th>Price</th></tr></thead><tbody>
            {report.imported.map((row, i) => <tr key={`${row.tier_name}-${i}`}><td>{row.tier_name}</td><td>{money(row.price_paise)}</td></tr>)}
          </tbody></table></div>
        )}
      </section>

      <section className="card report-section">
        <div className="section-heading"><h2>Deduplicated <span className="count">{report.deduplicated.length}</span></h2></div>
        {report.deduplicated.length === 0 ? <p className="muted">No duplicate rows found.</p> : (
          <div className="table-wrap"><table><thead><tr><th>Tier</th><th>Price</th><th>Duplicates</th><th>Reason</th></tr></thead><tbody>
            {report.deduplicated.map((row, i) => <tr key={`${row.tier_name}-${i}`}><td>{row.tier_name}</td><td>{money(row.price_paise)}</td><td>{row.duplicate_count}</td><td>{row.reason}</td></tr>)}
          </tbody></table></div>
        )}
      </section>

      <section className="card report-section full-width">
        <div className="section-heading"><h2>Rejected <span className="count">{report.rejected.length}</span></h2></div>
        {report.rejected.length === 0 ? <p className="muted">No rows rejected.</p> : (
          <div className="table-wrap"><table><thead><tr><th>Raw row</th><th>Reason</th></tr></thead><tbody>
            {report.rejected.map((row, i) => <tr key={i}><td><code>{JSON.stringify(row.raw_row)}</code></td><td>{row.reason}</td></tr>)}
          </tbody></table></div>
        )}
      </section>
    </div>
  );
}
