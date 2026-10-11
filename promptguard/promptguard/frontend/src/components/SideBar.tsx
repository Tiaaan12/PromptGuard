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
    <aside className="w-64 min-w-64 flex flex-col gap-5 px-3 py-5 bg-pg-sidebar border-r border-solid border-pg-border">
 
      <div className="flex items-center gap-2.5 px-1">

          <ShieldIcon size={60} />
      
        <span className="font-semibold text-[15px] text-pg-text tracking-tight">
          PromptGuard
        </span>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-pg-border-2 bg-pg-elevated text-pg-violet text-[13.5px] font-medium cursor-pointer transition-[background,border-color] duration-150 hover:bg-[#211C34] hover:border-pg-indigo"
      >
        <PlusIcon /> New Chat
      </button>

      <div className="flex-1 overflow-auto">
        <p className="px-1.5 mb-1.5 text-[10.5px] font-semibold text-pg-dim tracking-widest uppercase">
          Recent
        </p>
        <div className="flex flex-col gap-px">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`
                text-left px-2.5 py-2 rounded-lg border-none text-[13px] cursor-pointer
                truncate transition-[background,color] duration-150 font-sans
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
      <div className="flex items-center gap-1.5 px-1.5 pt-2 border-t border-pg-border text-pg-dim text-[11px]">
        <ShieldIcon size={11} />
        ML Protection Active
      </div>
    </aside>
  );
}
