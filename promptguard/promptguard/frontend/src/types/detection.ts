export type DetectionResult = {
  prediction: "INJECTION" | "BENIGN" | "ERROR";
  target: number | null;
  decision_score: number | null;
  error?: string;
};