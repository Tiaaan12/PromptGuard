import type { DetectionResult } from "../types/detection";

type Props = {
  result: DetectionResult;
};

export default function DetectionCard({ result }: Props) {
  const isInjection = result.prediction === "INJECTION";

  return (
    <div
      className={`
        rounded-xl border p-5
        ${
          isInjection
            ? "border-pg-danger-border bg-pg-danger-bg"
            : "border-pg-safe-border bg-pg-safe-bg"
        }
      `}
    >
      <h3
        className={
          isInjection
            ? "text-pg-danger"
            : "text-pg-safe"
        }
      >
        {isInjection
          ? "Potential Prompt Injection Detected"
          : "Prompt Appears Safe"}
      </h3>

      <div className="mt-3 text-sm text-pg-body">
        <p>Classification: {result.prediction}</p>
        <p>Target: {result.target}</p>
        <p>Decision Score: {result.decision_score}</p>
      </div>
    </div>
  );
}