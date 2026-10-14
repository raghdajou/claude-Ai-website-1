import { Fragment, useEffect, useState } from "react";

const LINKS = ["Labs", "Studio", "Openings", "Shop"];
const CONTACT_HREF = "mailto:hello@mainframe.co";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open]);

  const close = () => setOpen(false);

  return (
    <>
      <nav className="fixed inset-x-0 top-0 z-10 flex items-center justify-between px-5 py-4 text-white sm:px-8 sm:py-5">
        <a href="/" className="flex items-center gap-3">
          <span
            className="text-[21px] tracking-tight sm:text-[26px]"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            Mainframe®
          </span>
          <span
            className="select-none text-[25px] sm:text-[30px]"
            style={{ letterSpacing: "-0.02em" }}
            aria-hidden="true"
          >
            ✳︎
          </span>
        </a>

        <div className="hidden text-[23px] md:flex">
          {LINKS.map((label, i) => (
            <Fragment key={label}>
              {i > 0 && <span aria-hidden="true">,&nbsp;</span>}
              <a href={`#${label.toLowerCase()}`} className="transition-opacity hover:opacity-60">
                {label}
              </a>
            </Fragment>
          ))}
        </div>

        <a
          href={CONTACT_HREF}
          className="hidden text-[23px] underline underline-offset-2 transition-opacity hover:opacity-60 md:block"
        >
          Get in touch
        </a>

        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          aria-controls="mobile-menu"
          className="relative z-10 -mr-2 flex h-11 w-11 flex-col items-center justify-center gap-[5px] md:hidden"
        >
          <span
            className={`h-[2px] w-6 bg-white transition-transform duration-300 ${
              open ? "translate-y-[7px] rotate-45" : ""
            }`}
          />
          <span className={`h-[2px] w-6 bg-white transition-opacity duration-300 ${open ? "opacity-0" : ""}`} />
          <span
            className={`h-[2px] w-6 bg-white transition-transform duration-300 ${
              open ? "-translate-y-[7px] -rotate-45" : ""
            }`}
          />
        </button>
      </nav>

      <div
        id="mobile-menu"
        className="fixed inset-0 z-[9] flex flex-col justify-center gap-8 bg-black/90 px-8 text-white backdrop-blur-md transition-opacity duration-300 md:hidden"
        style={{ opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }}
        aria-hidden={!open}
      >
        {LINKS.map((label) => (
          <a key={label} href={`#${label.toLowerCase()}`} onClick={close} tabIndex={open ? 0 : -1} className="text-[32px] font-medium">
            {label}
          </a>
        ))}
        <a href={CONTACT_HREF} onClick={close} tabIndex={open ? 0 : -1} className="text-[32px] font-medium underline underline-offset-2">
          Get in touch
        </a>
      </div>
    </>
  );
}
