import { ShieldIcon } from "../icons";

function NavBar() {
  return (
    <header className="flex items-center gap-2.5 px-6 py-3.5 bg-pg-topbar border-b border-pg-border">
      <div
        className="w-[26px] h-[26px] rounded-[7px] flex items-center justify-center text-white shrink-0"
        style={{ background: "linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)" }}
      >
        <ShieldIcon size={13} />
      </div>
      <div>
        <div className="font-semibold text-[14.5px] text-pg-text leading-tight">
          PromptGuard
        </div>
        <div className="text-[11.5px] text-pg-dim leading-tight">
          Your AI conversation, protected by machine learning.
        </div>
      </div>
    </header>
  );
}


export default NavBar;