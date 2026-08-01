const BASE = "/api";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with ${res.status}`);
  }
  return res.json();
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: formData });
  return handle(res);
}

export async function analyzeDataset(datasetId, businessContext, focusColumns) {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dataset_id: datasetId,
      business_context: businessContext || null,
      focus_columns: focusColumns && focusColumns.length ? focusColumns : null,
    }),
  });
  return handle(res);
}

export function reportDownloadUrl(datasetId) {
  return `${BASE}/report/${datasetId}/download`;
}
