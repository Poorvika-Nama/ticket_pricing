import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import BookingPage from "./pages/BookingPage";
import ImportPage from "./pages/ImportPage";
import type { ImportReportData, SeatTier } from "./types";

const DEFAULT_TIERS: SeatTier[] = [
  { name: "Silver", price_paise: 15000, available_seats: 100 },
  { name: "Gold", price_paise: 25000, available_seats: 50 },
  { name: "Recliner", price_paise: 40000, available_seats: 20 },
];

export default function App() {
  const [importedTiers, setImportedTiers] = useState<SeatTier[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem("cinema-imported-tiers");
    if (stored) {
      try { setImportedTiers(JSON.parse(stored) as SeatTier[]); }
      catch { localStorage.removeItem("cinema-imported-tiers"); }
    }
  }, []);

  function handleImported(report: ImportReportData) {
    const tiers = report.imported.map((row) => ({ name: row.tier_name, price_paise: row.price_paise, available_seats: 0 }));
    setImportedTiers(tiers);
    localStorage.setItem("cinema-imported-tiers", JSON.stringify(tiers));
  }

  const tiers = [...DEFAULT_TIERS, ...importedTiers.filter((item) => !DEFAULT_TIERS.some((tier) => tier.name === item.name))];

  return (
    <div className="app-shell">
      <nav className="nav">
        <div className="brand"><span className="brand-icon">C</span><span>Cinema Pricing</span></div>
        <div className="nav-links"><NavLink to="/" end className={({ isActive }) => isActive ? "active" : ""}>Booking</NavLink><NavLink to="/import" className={({ isActive }) => isActive ? "active" : ""}>Price import</NavLink></div>
      </nav>
      <Routes>
        <Route path="/" element={<BookingPage tiers={tiers} />} />
        <Route path="/import" element={<ImportPage onImported={handleImported} />} />
      </Routes>
    </div>
  );
}
