import type { DetectionResult } from "./detection";
export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;

  detection?: DetectionResult;
  blocked?: boolean;
};

export type Conversation = {
  id: string;
  title: string;
  messages: Message[];
};