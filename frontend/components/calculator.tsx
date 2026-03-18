"use client";

import { useState } from "react";
import Image from "next/image";

const BRAND = {
  blue: "#0EB8D1",
  dark: "#222222",
};

export default function Calculator() {
  const [currentAge, setCurrentAge] = useState(30);
  const [lifeCover, setLifeCover] = useState(500000);
  const [premium, setPremium] = useState(1800);
  const [kiwisaverBalance, setKiwisaverBalance] = useState(100000);
  const [salary, setSalary] = useState(80000);
  const [kiwisaverRate, setKiwisaverRate] = useState(0.03);

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("en-NZ").format(val);
  };

  const parseNumber = (val: string) => {
    return Number(val.replace(/[^0-9.]/g, ""));
  };

  async function runProjection() {
    setLoading(true);
    setError("");
    setResults(null);

    try {
      const payload = {
        current_age: currentAge,
        life_cover: lifeCover,
        premium: premium,
        kiwisaver_balance: kiwisaverBalance,
        salary: salary,
        kiwisaver_rate: kiwisaverRate,
      };

      const res = await fetch("https://kiwisaver-calculator.onrender.com/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("API error");

      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError("Age must be below 65 for projection.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      {/* Banner Header */}
      <header className="header">
        <div className="logo-container">
          <Image
            src="/assets/logo_cropped.png"
            alt="Logo"
            width={120}
            height={120}
            style={{ objectFit: "contain" }}
          />
        </div>
        <div className="header-text">
          <h1>NZSaver Life Cover Offset Calculator</h1>
          <p className="tagline">Rethink today. Reinvest into tomorrow.</p>
        </div>
      </header>

      {/* Form */}
      <section className="form-card">
        <h2>Enter your details</h2>
        <div className="form-grid">
          <label>
            Current Age
            <div className="hint-circle" title="Enter your current age in years">?</div>
            <div className="input-wrapper">
              <input
                type="text"
                value={currentAge}
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
                value={formatCurrency(lifeCover)}
                onChange={(e) => setLifeCover(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Annual Premium
            <div className="hint-circle" title="Life cover yearly premium cost">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={formatCurrency(premium)}
                onChange={(e) => setPremium(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            KiwiSaver Balance
            <div className="hint-circle" title="Current KiwiSaver balance">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={formatCurrency(kiwisaverBalance)}
                onChange={(e) => setKiwisaverBalance(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            Salary
            <div className="hint-circle" title="Pre-tax annual salary">?</div>
            <div className="input-wrapper currency">
              <span className="prefix">$</span>
              <input
                type="text"
                value={formatCurrency(salary)}
                onChange={(e) => setSalary(parseNumber(e.target.value))}
              />
              <span className="suffix">NZD</span>
            </div>
          </label>

          <label>
            KiwiSaver Contribution
            <div className="hint-circle" title="Your contribution rate to KiwiSaver">?</div>
            <div className="input-wrapper percent">
              <input
                type="text"
                value={kiwisaverRate * 100}
                onChange={(e) => setKiwisaverRate(parseNumber(e.target.value) / 100)}
              />
              <span className="suffix">%</span>
            </div>
          </label>
        </div>
        
        <button onClick={runProjection} disabled={loading}>
          {loading ? "Running..." : "Run Projection"}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      {/* Results */}
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
              <p>Projected Savings of Insurance Premiums</p>
              <strong>${results?.total_savings?.toLocaleString() ?? "0"}</strong>
            </div>
            <div className="metric" style={{ borderTop: `4px solid ${BRAND.dark}` }}>
              <p>Projected Increase in KiwiSaver Balance</p>
              <strong>${results?.kiwisaver_increase?.toLocaleString() ?? "0"}</strong>
            </div>
            <div className="metric" style={{ borderTop: `4px solid ${BRAND.blue}` }}>
              <p>Projected Average Uplift Per Year</p>
              <strong>${results?.true_cost_per_year?.toLocaleString() ?? "0"}</strong>
            </div>
          </div>
        </section>
      )}

      <style jsx>{`
        .container {
          max-width: 900px;
          margin: 40px auto;
          padding: 20px;
          font-family: "Inter", Arial, sans-serif;
        }

        .header {
          display: flex;
          align-items: center;
          gap: 20px;
          background-color: ${BRAND.blue};
          padding: 5px 25px;
          border-radius: 12px;
          color: #fff;
          margin-bottom: 20px;
        }

        .logo-container {
          flex-shrink: 0;
          display: flex;
          align-items: center;
        }

        .header-text h1 {
          font-size: 20px;
          margin: 0;
        }

        .tagline {
          font-size: 13px;
          font-weight: 500;
          margin-top: 2px;
          opacity: 0.9;
        }

        .form-card, .results-card {
          background: #ffffff;
          padding: 25px 30px;
          border-radius: 12px;
          box-shadow: 0 5px 20px rgba(0,0,0,0.1);
          margin-bottom: 25px;
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
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
          margin-top: 20px;
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
          border: 1px solid #ccc;
          transition: all 0.2s ease;
        }

        .currency input {
          padding-left: 25px;
        }

        .prefix {
          position: absolute;
          left: 10px;
          color: #666;
          font-weight: 500;
        }

        .suffix {
          position: absolute;
          right: 12px;
          color: #999;
          font-size: 12px;
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
          box-shadow: 0 0 6px rgba(14,184,209,0.2);
        }

        button {
          padding: 14px 24px;
          background: ${BRAND.blue};
          color: #fff;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.2s ease;
          width: 100%;
          max-width: 300px;
        }

        button:hover:not(:disabled) {
          background: #0aaec2;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }

        .metric {
          background: #f9f9f9;
          padding: 20px;
          border-radius: 10px;
          text-align: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .metric p {
          margin: 0 0 10px 0;
          font-size: 13px;
          color: #666;
        }

        .metric strong {
          font-size: 22px;
          color: ${BRAND.dark};
        }

        .error {
          color: #d32f2f;
          margin-top: 15px;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
}