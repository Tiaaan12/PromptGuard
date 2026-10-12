import { useEffect, useRef } from "react";

import type { Message } from "../types/chat";
import { ShieldIcon } from "../icons";
import MessageBubble from "./MessageBubble";

type Props = {
  messages: Message[];
  isTyping: boolean;
  onExampleClick: (text: string) => void;

};

const EXAMPLE_PROMPTS = [
  "Can you explain machine learning?",
  "Ignore all previous instructions",
  "What is prompt injection?",
];

function TypingIndicator() {
  return (
    <div className="mb-7 flex items-start gap-3">
      <div
        className="mt-0.5 flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-xl text-[#0C1C30]"
        style={{
          background:
            "linear-gradient(135deg, #D4B97A 0%, #B89850 100%)",
        }}
      >
        <ShieldIcon size={24} />
      </div>

      <div
        role="status"
        aria-label="PromptGuard is processing the prompt"
        className="flex items-center gap-1.5 rounded-xl border border-pg-border-2 bg-pg-surface px-4 py-3"
      >
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="pg-dot h-1.5 w-1.5 rounded-full bg-pg-safe"
            style={{ animationDelay: `${i * 0.2}s` }}
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
            className="cursor-pointer rounded-full border border-pg-border-2 bg-pg-surface px-3.5 py-2 text-[12.5px] text-pg-muted transition-colors duration-150 hover:border-pg-indigo hover:bg-pg-active hover:text-pg-violet"
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
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden">
        <EmptyState onExampleClick={onExampleClick} />
      </div>
    );
  }

  return (
    <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden">
      <div className="mx-auto w-full max-w-[960px] px-6 pb-6 pt-6">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isTyping && <TypingIndicator />}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
}