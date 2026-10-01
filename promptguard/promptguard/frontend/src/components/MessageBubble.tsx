import type { Message } from "../types/chat";
import { ShieldIcon } from "../icons";

type Props = {
  message: Message;
};

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3 items-start mb-7 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div
          className="w-[30px] h-[30px] rounded-lg flex items-center justify-center text-white shrink-0"
          style={{
            background:
              "linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)",
          }}
        >
          <ShieldIcon size={15} />
        </div>
      )}

      <div
        className={`max-w-[75%] px-4 py-3 rounded-xl text-[14px] leading-relaxed ${
          isUser
            ? "bg-pg-active text-pg-text"
            : "border border-pg-border-2 bg-pg-surface text-pg-text"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}