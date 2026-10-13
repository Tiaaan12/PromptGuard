import type { Conversation } from "../types/chat";
import { ShieldIcon, PlusIcon } from "../icons";

type Props = {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
};

export default function Sidebar({ conversations, activeId, onSelect, onNewChat }: Props) {
  return (
    <aside className="flex max-h-[38dvh] w-full min-w-0 flex-col gap-4 overflow-y-auto overflow-x-hidden border-b border-solid border-pg-border bg-pg-sidebar px-4 py-4 md:max-h-none md:w-64 md:min-w-64 md:shrink-0 md:gap-5 md:border-b-0 md:border-r md:px-3 md:py-5">
 
      <div className="flex min-w-0 items-center gap-2.5 px-1">

          <ShieldIcon size={60} />
      
        <span className="min-w-0 font-semibold text-[15px] tracking-tight text-pg-text">
          PromptGuard
        </span>
      </div>

      <button
        onClick={onNewChat}
        className="flex w-full items-center gap-2 rounded-lg border border-pg-border-2 bg-pg-elevated px-3 py-2.5 text-[13.5px] font-medium text-pg-violet transition-[background,border-color] duration-150 cursor-pointer hover:border-pg-indigo hover:bg-[#211C34] md:w-auto"
      >
        <PlusIcon /> New Chat
      </button>

      <div className="min-h-0 flex-1 overflow-auto">
        <p className="mb-1.5 px-1.5 text-[10.5px] font-semibold uppercase tracking-widest text-pg-dim">
          Recent
        </p>
        <div className="flex flex-col gap-px">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`
                min-w-0 rounded-lg border-none px-2.5 py-2 text-left text-[13px] font-sans cursor-pointer
                truncate transition-[background,color] duration-150
                ${activeId === conv.id
                  ? "bg-pg-active text-pg-violet font-medium"
                  : "bg-transparent text-pg-muted hover:bg-pg-hover hover:text-[#A78BFA]"}
              `}
            >
              {conv.title}
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-1.5 border-t border-pg-border px-1.5 pt-2 text-[11px] text-pg-dim">
        <ShieldIcon size={11} />
        ML Protection Active
      </div>
    </aside>
  );
}
