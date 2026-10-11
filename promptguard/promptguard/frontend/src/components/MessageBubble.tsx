import type { Message } from "../types/chat";
import { ShieldIcon } from "../icons";
import DetectionCard from "./DetectionCard";

type Props = {
  message: Message;
};

export default function MessageBubble({ message }: Props) {
  if (message.role === "user") {
    return (
      <div className="mb-7 flex justify-end">
        <div
          className="max-w-[75%] rounded-[16px_16px_4px_16px] px-4 py-2.5 text-[14px] font-medium leading-relaxed text-[#0C1C30]"
          style={{
            background:
              "linear-gradient(135deg, #B89850 0%, #D4B97A 100%)",
            boxShadow: "0 2px 12px rgba(184,152,80,0.2)",
          }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-7 flex items-start gap-3">
      <div
        className="mt-0.5 flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-xl text-[#0C1C30]"
        style={{
          background:
            "linear-gradient(135deg, #D4B97A 0%, #B89850 100%)",
        }}
      >
        <ShieldIcon size={17} />
      </div>

      <div className="min-w-0 flex-1">
        {message.detection && (
          <DetectionCard
            result={message.detection}
            blocked={message.blocked ?? false}
          />
        )}

        {message.content && (
          <p className="text-[14px] leading-[1.7] text-pg-body">
            {message.content}
          </p>
        )}
      </div>
    </div>
  );
}