import { useState } from "react";
import type { DetectionResult } from "../types/detection";
import { ShieldIcon } from "../icons";

type Props = {
  result: DetectionResult;
  blocked?: boolean;
};

export default function DetectionCard({
  result,
  blocked = false,
}: Props) {
  const [showAnalysis, setShowAnalysis] = useState(false);

  if (result.prediction === "ERROR") {
    return (
      <div className="mb-2.5 rounded-xl border border-pg-border-2 bg-pg-surface p-4 text-sm text-pg-body">
        <p className="font-semibold">Detection unavailable</p>
        <p className="mt-1">
          {result.error ?? "An error occurred during analysis."}
        </p>
      </div>
    );
  }

  const isInjection = result.prediction === "INJECTION";

  const score =
    result.decision_score == null
      ? "Unavailable"
      : result.decision_score.toFixed(3);

  const analysis = (
    <div className="mt-3 rounded-lg border border-pg-border-2 bg-pg-analysis p-3 font-mono text-[11.5px] leading-relaxed text-pg-muted">
  <p className="mb-2 font-medium text-pg-violet">
    Why This Prediction?
  </p>

  <p>Model: Linear SVM</p>
  <p>Features: Character TF-IDF (3–5 grams)</p>
  <p>Training version: V3</p>
  <p>
    Predicted class:{" "}
    {result.target == null
      ? "Unavailable"
      : result.target === 0
        ? "Benign (0)"
        : "Injection (1)"}
  </p>
  <p>Decision boundary: 0.0</p>
  <p>
    Decision score:{" "}
    {result.decision_score == null
      ? "Unavailable"
      : result.decision_score.toFixed(3)}
  </p>

  {result.decision_score != null && (
    <p className="mt-2">
      {result.decision_score > 0
        ? "The positive decision score places this prompt on the injection side of the SVM decision boundary."
        : result.decision_score < 0
          ? "The negative decision score places this prompt on the benign side of the SVM decision boundary."
          : "The decision score is at the SVM decision boundary."}
    </p>
  )}

  <p className="mt-2">
    The model uses learned character patterns to classify the prompt.
    The decision score is not a calibrated probability.
  </p>
</div>
  );

  if (!isInjection) {
    return (
      <div className="mb-2.5 rounded-[10px] border border-pg-safe-border bg-pg-safe-bg px-3.5 py-2.5 text-[13px]">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-pg-safe text-pg-bg">
            ✓
          </span>

          <span className="font-medium text-pg-safe">Safe Prompt</span>
          <span className="text-pg-safe-border">·</span>
          <span className="font-mono text-xs text-pg-safe-mid">
            Benign
          </span>

          <button
            type="button"
            onClick={() => setShowAnalysis((value) => !value)}
            aria-expanded={showAnalysis}
            className="ml-auto text-xs text-pg-safe hover:underline"
          >
            {showAnalysis ? "Hide Analysis ↑" : "View Analysis ↓"}
          </button>
        </div>

        {showAnalysis && analysis}
      </div>
    );
  }

  return (
    <div className="mb-2.5 rounded-[10px] border border-pg-danger-border bg-pg-danger-bg px-3.5 py-3 text-[13px]">
      <div className="mb-2.5 flex items-center gap-2">
        <span className="flex items-center text-pg-danger">
          <ShieldIcon size={16} />
        </span>

        <span className="font-semibold text-pg-danger">
          Potential Prompt Injection Detected
        </span>
      </div>

      <div className="mb-3 grid grid-cols-2 gap-x-5 gap-y-2">
        <div>
          <span className="font-mono text-[11px] text-pg-muted">
            Classification:
          </span>
          <p className="font-mono text-xs text-pg-body">
            Prompt Injection
          </p>
        </div>

        <div>
          <span className="font-mono text-[11px] text-pg-muted">
            Target:
          </span>
          <p className="font-mono text-xs text-pg-body">
            {result.target ?? "Unavailable"}
          </p>
        </div>

        <div>
          <span className="font-mono text-[11px] text-pg-muted">
            Model score:
          </span>
          <p className="font-mono text-xs text-pg-body">{score}</p>
        </div>

        <div>
          <span className="font-mono text-[11px] text-pg-muted">
            Action:
          </span>
          <p className="font-mono text-xs font-semibold text-pg-danger">
            {blocked ? "Blocked" : "Flagged"}
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setShowAnalysis((value) => !value)}
        aria-expanded={showAnalysis}
        className="rounded-md border border-pg-danger-border px-3 py-1.5 text-xs font-medium text-pg-danger transition-colors hover:bg-black/10"
      >
        {showAnalysis ? "Hide Analysis ↑" : "View Analysis ↓"}
      </button>

      {showAnalysis && analysis}
    </div>
  );
}