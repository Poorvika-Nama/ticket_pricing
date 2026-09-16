import { useState } from "react";
import Papa from "papaparse";
import { importPriceList } from "../api";
import type { ImportReportData } from "../types";

type Props = { onImported: (report: ImportReportData) => void };

type CsvRow = { tier_name?: string; price?: string };

export default function PriceImportForm({ onImported }: Props) {
  const [fileName, setFileName] = useState("");
  const [rows, setRows] = useState<Array<{ tier_name: string; price: unknown }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFile(file?: File) {
    if (!file) return;
    setFileName(file.name);
    setError("");
    Papa.parse<CsvRow>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        const parsed = result.data
          .filter((row) => row.tier_name !== undefined && row.price !== undefined)
          .map((row) => ({ tier_name: row.tier_name!.trim(), price: row.price }));
        setRows(parsed);
      },
      error: (parseError) => setError(`Could not parse CSV: ${parseError.message}`),
    });
  }

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const report = await importPriceList(rows);
      // Shared state is persisted in localStorage by App so imported tiers populate booking after navigation/reload.
      onImported(report);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import price list.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card import-form">
      <div className="section-heading"><div><span className="eyebrow">CSV importer</span><h2>Bring in a price list</h2></div></div>
      <label className="file-drop">
        <input type="file" accept=".csv,text/csv" onChange={(e) => handleFile(e.target.files?.[0])} />
        <span className="upload-icon">↑</span>
        <strong>{fileName || "Choose a CSV file"}</strong>
        <small>Expected columns: tier_name, price</small>
      </label>
      {rows.length > 0 && <p className="file-meta">Parsed {rows.length} row{rows.length === 1 ? "" : "s"}. Ready to send.</p>}
      {error && <div className="error" role="alert">{error}</div>}
      {loading && <p className="loading">Cleaning and importing…</p>}
      <button className="primary" type="button" disabled={!rows.length || loading} onClick={submit}>
        {loading ? "Importing…" : "Clean and import"}
      </button>
    </section>
  );
}
