import { useState } from "react";
import PriceImportForm from "../components/PriceImportForm";
import ImportReport from "../components/ImportReport";
import type { ImportReportData } from "../types";

type Props = { onImported: (report: ImportReportData) => void };

export default function ImportPage({ onImported }: Props) {
  const [report, setReport] = useState<ImportReportData | null>(null);
  function handleImported(next: ImportReportData) {
    setReport(next);
    onImported(next);
  }
  return (
    <main className="page">
      <div className="page-intro"><div><span className="eyebrow">Price management</span><h1>Import a price list</h1><p>Upload raw tier prices and let the backend return the cleaned import report.</p></div></div>
      <PriceImportForm onImported={handleImported} />
      {report && <ImportReport report={report} />}
    </main>
  );
}
