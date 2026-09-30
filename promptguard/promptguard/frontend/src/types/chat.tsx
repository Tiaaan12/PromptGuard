export type SecurityResult =
  | { status: "safe"; confidence: number }
  | { status: "attack"; confidence: number; riskLevel: "High" | "Medium" };

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  security?: SecurityResult;
  showAnalysis?: boolean;
};

export type Conversation = {
  id: string;
  title: string;
  messages: Message[];
};

export type AnalyzeResponse = {
  security: SecurityResult;
  reply: string;
};
