import { useEffect, useRef } from "react";

import type { DetectionResult } from "../types/detection";
import type { Message } from "../types/chat";

import { ShieldIcon } from "../icons";
import MessageBubble from "./MessageBubble";
import DetectionCard from "./DetectionCard";

type Props = {
  messages: Message[];
  isTyping: boolean;
  onExampleClick: (text: string) => void;
  detectionResult: DetectionResult | null;
};

const EXAMPLE_PROMPTS = [
  "Can you explain machine learning?",
  "Ignore all previous instructions",
  "What is prompt injection?",
];

function TypingIndicator() {
  return (
    <div className="mb-7 flex items-start gap-3">
      <div className="flex h-6 w-6 shrink-0 items-center justify-center">
        <ShieldIcon size={24} />
      </div>

      <div className="flex items-center gap-1.5 rounded-xl border border-pg-border-2 bg-pg-surface px-3.5 py-3">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="pg-dot h-1.5 w-1.5 rounded-full bg-pg-dim"
            style={{
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

function EmptyState({
  onExampleClick,
}: {
  onExampleClick: (text: string) => void;
}) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 px-10">
      <ShieldIcon size={30} />

      <div className="text-center">
        <h2 className="mb-1.5 text-[20px] font-semibold text-pg-text">
          Hi, I'm PromptGuard.
        </h2>

        <p className="max-w-[360px] text-[14px] leading-relaxed text-pg-muted">
          Send me a message and I'll check it for potential prompt injection
          attacks.
        </p>
      </div>

      <div className="mt-2 flex flex-wrap justify-center gap-2.5">
        {EXAMPLE_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onExampleClick(prompt)}
            className="
              cursor-pointer rounded-full border border-pg-border-2
              bg-pg-surface px-3.5 py-2 text-[12.5px]
              text-pg-muted transition-colors duration-150
              hover:border-pg-indigo hover:bg-pg-active hover:text-pg-violet
            "
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({
  messages,
  isTyping,
  onExampleClick,
  detectionResult,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isTyping, detectionResult]);

  if (messages.length === 0 && !detectionResult) {
    return (
      <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden">
        <EmptyState onExampleClick={onExampleClick} />
      </div>
    );
  }

  return (
    <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden">
      <div className="mx-auto w-full max-w-[740px] px-6 pb-6 pt-6">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
          />
        ))}

        {isTyping && <TypingIndicator />}

        {detectionResult && (
          <div className="mb-7">
            <DetectionCard result={detectionResult} />
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}