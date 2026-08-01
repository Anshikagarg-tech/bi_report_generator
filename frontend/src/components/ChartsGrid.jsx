export default function ChartsGrid({ charts }) {
  if (!charts || charts.length === 0) return null;
  return (
    <div className="charts-grid">
      {charts.map((chart) => (
        <figure className="chart-card" key={chart.filename}>
          <img src={chart.url} alt={chart.title} loading="lazy" />
          <figcaption>{chart.title}</figcaption>
        </figure>
      ))}
    </div>
  );
}
