import KpiCards from "./KpiCards";
import ChartsGrid from "./ChartsGrid";
import { reportDownloadUrl } from "../api/client";

export default function ReportView({ report }) {
  return (
    <div className="report">
      <div className="report__header">
        <div>
          <h1>{report.title}</h1>
          <p className="report__meta">
            Generated {new Date(report.generated_at).toLocaleString()}
          </p>
        </div>
        <a className="btn btn--secondary" href={reportDownloadUrl(report.dataset_id)} download>
          Download Markdown
        </a>
      </div>

      <section>
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
      </section>

      <KpiCards kpis={report.kpis} />

      <ChartsGrid charts={report.charts} />

      {report.sections.map((s, i) => (
        <section key={i}>
          <h2>{s.heading}</h2>
          <p>{s.content}</p>
        </section>
      ))}

      {report.data_quality_notes?.length > 0 && (
        <section>
          <h2>Data Quality Notes</h2>
          <ul>
            {report.data_quality_notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </section>
      )}

      {report.recommendations?.length > 0 && (
        <section>
          <h2>Recommendations</h2>
          <ul>
            {report.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
