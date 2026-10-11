import { ShieldIcon } from "../icons";

function NavBar() {
  return (
    <header className="flex items-center gap-2.5 px-6 py-3.5 bg-pg-topbar border-b border-solid border-pg-border">
        <ShieldIcon size={36} />
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