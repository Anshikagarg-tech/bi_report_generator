export default function KpiCards({ kpis }) {
  if (!kpis || kpis.length === 0) return null;
  return (
    <div className="kpi-grid">
      {kpis.map((kpi, i) => (
        <div className="kpi-card" key={i}>
          <div className="kpi-card__label">{kpi.label}</div>
          <div className="kpi-card__value">{kpi.value}</div>
          {kpi.delta && <div className="kpi-card__delta">{kpi.delta}</div>}
        </div>
      ))}
    </div>
  );
}
