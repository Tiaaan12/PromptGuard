import { ShieldIcon } from "../icons";

function NavBar() {
  return (
    <header className="flex items-center gap-2.5 border-b border-solid border-pg-border bg-pg-topbar px-4 py-3 sm:px-6 sm:py-3.5">
        <ShieldIcon size={36} />
      <div className="min-w-0">
        <div className="text-[14px] font-semibold leading-tight text-pg-text sm:text-[14.5px]">
          PromptGuard
        </div>
        <div className="text-[10px] leading-tight text-pg-dim sm:text-[11.5px]">
          Your AI conversation, protected by machine learning.
        </div>
      </div>
    </header>
  );
}


export default NavBar;