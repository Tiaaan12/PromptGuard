import { useRef } from "react";

import { ShieldIcon, SendIcon } from "../icons";

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
};

export default function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
}: Props) {

  const textareaRef = useRef<HTMLTextAreaElement>(null);


  function handleChange(
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) {
    onChange(e.target.value);

    e.target.style.height = "auto";

    e.target.style.height =
      Math.min(e.target.scrollHeight, 160) + "px";
  }


  function handleKeyDown(
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  }


  const canSend =
    value.trim().length > 0 && !disabled;


  return (
    <div className="border-t border-solid border-pg-border bg-pg-bg px-3 pb-3 pt-3 sm:px-6 sm:pb-4 sm:pt-3">

      <div className="mx-auto max-w-full sm:max-w-[740px]">

 
        <div
          className="
            flex items-end gap-2
            rounded-[14px]
            border border-pg-border-2
            bg-pg-surface
            px-3 py-2 pr-2
            transition-[border-color,box-shadow]
            duration-150
          "
          style={{
            boxShadow: "0 2px 16px rgba(0,0,0,0.4)",
          }}

          onFocusCapture={(e) => {
            e.currentTarget.style.borderColor =
              "#D4B97A";

            e.currentTarget.style.boxShadow =
              "0 2px 16px rgba(212,185,122,0.15)";
          }}

          onBlurCapture={(e) => {
            e.currentTarget.style.borderColor =
              "#2A2438";

            e.currentTarget.style.boxShadow =
              "0 2px 16px rgba(0,0,0,0.4)";
          }}
        >

          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Message PromptGuard…"
            rows={1}

            className="
              flex-1
              min-w-0
              bg-transparent
              border-none
              outline-none
              text-[16px]
              sm:text-[14px]
              text-pg-text
              placeholder:text-pg-dim
              font-sans
              leading-relaxed
              py-0.5
              max-h-40
              overflow-y-auto
            "

            style={{
              caretColor: "#D4B97A",
            }}
          />

          <button
            onClick={onSend}
            disabled={!canSend}

            className="
              h-11
              w-11
              sm:h-[34px]
              sm:w-[34px]
              rounded-lg
              border-none
              flex
              items-center
              justify-center
              shrink-0
              transition-[background,color,box-shadow]
              duration-150
              cursor-pointer
              disabled:cursor-default
              touch-manipulation
            "

            style={{
              background: canSend
                ? "linear-gradient(135deg, #D4B97A 0%, #B89850 100%)"
                : "#1E1A2E",

              color: canSend
                ? "#0C1C30"
                : "#3E3020",

              boxShadow: canSend
                ? "0 2px 8px rgba(212,185,122,0.35)"
                : "none",
            }}
          >
            <SendIcon />
          </button>

        </div>
        <div className="mt-2 flex items-center justify-center gap-1.5 text-[10px] text-pg-dim sm:text-[11px]">
          <ShieldIcon size={11} />

          Protected by PromptGuard ML
        </div>

      </div>

    </div>
  );
}