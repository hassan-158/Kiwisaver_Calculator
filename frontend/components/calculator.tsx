"use client";

import { useState } from "react";
import Image from "next/image";

const BRAND = {
  blue: "#0EB8D1",
  dark: "#222222",
  bg: "#F8FAFC",
  lightBlueBg: "#F0FDFA",
};

export default function Calculator() {
  // Inputs start blank
  const [currentAge, setCurrentAge] = useState<number | "">("");
  const [lifeCover, setLifeCover] = useState<number | "">("");
  const [premium, setPremium] = useState<number | "">("");
  const [kiwisaverBalance, setKiwisaverBalance] = useState<number | "">("");
  const [salary, setSalary] = useState<number | "">("");
  const [kiwisaverRate, setKiwisaverRate] = useState(0);
  const [kiwisaverRateInput, setKiwisaverRateInput] = useState("");

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat("en-NZ").format(val);

  const parseNumber = (val: string) => Number(val.replace(/[^0-9.]/g, ""));

  async function runProjection() {
    setLoading(true);
    setError("");
    setResults(null);

    // Check for missing inputs
    if (
      currentAge === "" ||
      lifeCover === "" ||
      premium === "" ||
      kiwisaverBalance === "" ||
      salary === "" ||
      kiwisaverRateInput === ""
    ) {
      setError("Please fill in all inputs.");
      setLoading(false);
      return;
    }

    try {
      const payload = {
        current_age: currentAge,
        life_cover: lifeCover,
        premium: premium,
        kiwisaver_balance: kiwisaverBalance,
        salary: salary,
        kiwisaver_rate: kiwisaverRate,
      };

      const res = await fetch(
        "https://kiwisaver-calculator.onrender.com/calculate",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!res.ok) throw new Error("API error");

      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError("Age must be under 65 to run the projection.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <div className="logo-container">
            <Image
              src="/assets/logo_cropped.png"
              alt="Logo"
              width={280}
              height={100}
              style={{ objectFit: "contain" }}
              priority
            />
          </div>
          <p className="tagline-inside">Rethink today. Reinvest into tomorrow.</p>
        </div>
      </header>

      <h1 className="main-heading">
        NZSaver Life Cover <span style={{ color: BRAND.blue }}>Offset Calculator</span>
      </h1>

      <section className="form-card">
        <h2>Enter your details</h2>
        <div className="form-grid">
          <label>
            Current Age
            <div className="hint-circle" title="Enter your current age in years">?</div>
            <div className="input-wrapper">
              <input
                type="text"
                value={currentAge === "" ? "" : currentAge}
                onChange={(e) => setCurrentAge(parseNumber(e.target.value))}
              />
            </div>
          </label>

          <label>
            Life Cover
            <div className="hint-circle" title="Total life cover required">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={lifeCover === "" ? "" : formatCurrency(lifeCover)}
                onChange={(e) => setLifeCover(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Annual Premium
            <div className="hint-circle" title="Yearly cost of life cover">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={premium === "" ? "" : formatCurrency(premium)}
                onChange={(e) => setPremium(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Current KiwiSaver Balance
            <div className="hint-circle" title="Current KiwiSaver account balance">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={kiwisaverBalance === "" ? "" : formatCurrency(kiwisaverBalance)}
                onChange={(e) => setKiwisaverBalance(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Pre-tax Annual Salary
            <div className="hint-circle" title="Your annual salary before tax">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={salary === "" ? "" : formatCurrency(salary)}
                onChange={(e) => setSalary(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Employee & Employer KiwiSaver
            <div className="hint-circle" title="Combined contribution rate from employee and employer">?</div>
            <div className="input-wrapper percent">
              <input
                type="text"
                value={kiwisaverRateInput}
                onChange={(e) => {
                  const val = e.target.value;
                  if (/^\d*\.?\d*$/.test(val)) {
                    setKiwisaverRateInput(val);
                    const parsed = parseFloat(val);
                    setKiwisaverRate(isNaN(parsed) ? 0 : parsed / 100);
                  }
                }}
              />
              <span className="suffix">%</span>
            </div>
          </label>
        </div>

        <button className="submit-btn" onClick={runProjection} disabled={loading}>
          {loading ? "Running..." : "Run Projection"}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      {results && (
        <section className="results-card">
          <div className="results-header">
            <h2>Results</h2>
            <div className="age-notice">
              <span className="icon">⏱</span>
              Calculated at age 65
            </div>
          </div>

          <div className="metrics-grid">
            <div className="metric" style={{ borderTop: `4px solid ${BRAND.blue}` }}>
              <p>Projected Savings of Insurance Premiums by Age 65</p>
              <strong>${results?.total_savings?.toLocaleString() ?? "0"}</strong>
            </div>
            <div
              className="metric"
              style={{
                borderTop: `4px solid ${BRAND.dark}`,
                background: BRAND.lightBlueBg,
              }}
            >
              <p>Projected Increase in KiwiSaver Balance by Age 65</p>
              <strong>${results?.kiwisaver_increase?.toLocaleString() ?? "0"}</strong>
              <div
                style={{
                  fontSize: "13px",
                  color: "#16a34a",
                  marginTop: "4px",
                  fontWeight: "700",
                }}
              >
                +{results?.kiwisaver_increase_pct?.toFixed(2) ?? "0"}%
              </div>
            </div>
            <div className="metric" style={{ borderTop: `4px solid ${BRAND.blue}` }}>
              <p>Projected Average Uplift Per Year to Age 65</p>
              <strong>${results?.true_cost_per_year?.toLocaleString() ?? "0"}</strong>
            </div>
          </div>
        </section>
      )}

      <style jsx>{`
        :global(body) {
          background-color: ${BRAND.bg} !important;
          margin: 0;
          font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .container {
          max-width: 1000px;
          margin: 40px auto;
          padding: 20px;
        }

        .header {
          background-color: ${BRAND.blue};
          padding: 15px 30px;
          border-radius: 12px;
          margin-bottom: 25px;
          display: flex;
          justify-content: center;
          align-items: center;
          box-shadow: 0 4px 15px rgba(14, 184, 209, 0.2);
        }

        .header-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 5px;
        }

        .tagline-inside {
          font-size: 15px;
          font-weight: 500;
          color: #ffffff;
          margin: 0;
          opacity: 0.95;
          font-style: italic;
        }

        .main-heading {
          font-size: 28px;
          color: ${BRAND.dark};
          margin-bottom: 25px;
          font-weight: 800;
          padding-left: 5px;
          letter-spacing: -0.02em;
        }

        .form-card,
        .results-card {
          background: #ffffff;
          padding: 25px 30px;
          border-radius: 12px;
          box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
          margin-bottom: 25px;
          border: 1px solid #eef2f6;
        }

        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .age-notice {
          display: flex;
          align-items: center;
          gap: 6px;
          background: #f1f5f9;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          color: #475569;
          border: 1px solid #e2e8f0;
        }

        h2 {
          margin: 0;
          color: ${BRAND.dark};
          font-size: 20px;
          font-weight: 700;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 20px;
          margin-top: 20px;
          margin-bottom: 25px;
        }

        label {
          position: relative;
          display: flex;
          flex-direction: column;
          font-weight: 600;
          font-size: 14px;
          color: #444;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
          margin-top: 10px;
        }

        .input-wrapper input {
          width: 100%;
          padding: 10px 12px;
          font-size: 15px;
          border-radius: 6px;
          border: 1px solid #cbd5e1;
          transition: all 0.2s ease;
          font-family: inherit;
        }

        .currency input {
          padding-left: 25px;
        }
        .prefix {
          position: absolute;
          left: 10px;
          color: #64748b;
          font-weight: 500;
        }
        .suffix {
          position: absolute;
          right: 12px;
          color: #94a3b8;
          font-size: 11px;
          font-weight: bold;
          pointer-events: none;
        }

        .hint-circle {
          position: absolute;
          top: -4px;
          right: -4px;
          background-color: ${BRAND.blue};
          color: white;
          border-radius: 50%;
          width: 16px;
          height: 16px;
          font-size: 10px;
          text-align: center;
          line-height: 16px;
          cursor: pointer;
        }

        input:focus {
          outline: none;
          border-color: ${BRAND.blue};
          box-shadow: 0 0 0 3px rgba(14, 184, 209, 0.1);
        }

        .submit-btn {
          padding: 14px 24px;
          background: ${BRAND.blue};
          color: #fff;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          font-weight: 700;
          transition: all 0.2s ease;
          width: 100%;
          max-width: 300px;
        }

        .submit-btn:hover:not(:disabled) {
          background: #0aaec2;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(14, 184, 209, 0.25);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }

        .metric {
          background: #f8fafc;
          padding: 20px;
          border-radius: 10px;
          text-align: center;
          border: 1px solid #f1f5f9;
        }

        .metric p {
          margin: 0 0 10px 0;
          font-size: 13px;
          color: #64748b;
          font-weight: 500;
        }
        .metric strong {
          font-size: 22px;
          color: ${BRAND.dark};
          font-weight: 800;
        }

        .error {
          color: #ef4444;
          margin-top: 15px;
          font-size: 14px;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}