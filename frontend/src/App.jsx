import { useState } from "react";
import FileUpload from "./components/FileUpload";
import LoadingState from "./components/LoadingState";
import ReportView from "./components/ReportView";
import { analyzeDataset } from "./api/client";

export default function App() {
  const [dataset, setDataset] = useState(null); // upload response
  const [businessContext, setBusinessContext] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  async function handleAnalyze() {
    if (!dataset) return;
    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeDataset(dataset.dataset_id, businessContext);
      setReport(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  }

  function reset() {
    setDataset(null);
    setReport(null);
    setBusinessContext("");
    setError(null);
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>📊 Automated BI Report Generator</h1>
        <p>Upload tabular data. Get a GenAI-drafted business intelligence report in seconds.</p>
      </header>

      {error && <div className="alert alert--error">{error}</div>}

      {!report && (
        <div className="panel">
          {!dataset ? (
            <FileUpload onUploaded={setDataset} onError={setError} />
          ) : (
            <div className="dataset-summary">
              <h3>{dataset.filename}</h3>
              <p>
                {dataset.rows.toLocaleString()} rows &times; {dataset.columns} columns
              </p>

              <div className="preview-table-wrap">
                <table className="preview-table">
                  <thead>
                    <tr>
                      {dataset.column_names.map((c) => (
                        <th key={c}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dataset.preview.map((row, i) => (
                      <tr key={i}>
                        {dataset.column_names.map((c) => (
                          <td key={c}>{row[c]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <label className="field-label" htmlFor="context">
                Business context (optional) — helps the report focus on what matters
              </label>
              <textarea
                id="context"
                rows={3}
                placeholder="e.g. This is quarterly retail sales across 4 regions. We care about revenue growth and underperforming regions."
                value={businessContext}
                onChange={(e) => setBusinessContext(e.target.value)}
              />

              <div className="actions">
                <button className="btn" onClick={handleAnalyze} disabled={analyzing}>
                  {analyzing ? "Generating report..." : "Generate BI Report"}
                </button>
                <button className="btn btn--ghost" onClick={reset} disabled={analyzing}>
                  Choose different file
                </button>
              </div>

              {analyzing && <LoadingState />}
            </div>
          )}
        </div>
      )}

      {report && (
        <>
          <ReportView report={report} />
          <div className="actions actions--center">
            <button className="btn btn--ghost" onClick={reset}>
              Analyze another dataset
            </button>
          </div>
        </>
      )}

      <footer className="app__footer">
        Built with FastAPI + Claude &middot; Charts rendered server-side from a verified statistical profile
      </footer>
    </div>
  );
}
