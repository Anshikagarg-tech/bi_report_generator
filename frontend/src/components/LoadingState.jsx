const STEPS = [
  "Profiling columns and data types...",
  "Computing distributions, correlations & trends...",
  "Rendering charts...",
  "Drafting narrative report with Claude...",
];

import { useEffect, useState } from "react";

export default function LoadingState() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setStep((s) => (s + 1) % STEPS.length), 1800);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="loading">
      <div className="spinner" />
      <p>{STEPS[step]}</p>
    </div>
  );
}
