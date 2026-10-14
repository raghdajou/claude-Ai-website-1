import { useEffect, useState } from "react";
import { useTypewriter } from "../hooks/useTypewriter";

const EMAIL = "hello@mainframe.co";
const TYPED_TEXT = "Glad you stopped in. Good taste tends to find us. Now, what are we building?";

const ACTIONS = [
  { label: "Pitch us an idea", subject: "An idea" },
  { label: "Come work here", subject: "Working at Mainframe" },
  { label: "Send a brief hello", subject: "Hello" },
  { label: "See how we operate", subject: "How you operate" },
];

const PILL =
  "inline-flex items-center justify-center whitespace-nowrap rounded-full border px-4 py-[0.3em] mx-[0.2em] mb-[0.4em] text-[13px] transition-colors duration-200 sm:px-5 sm:text-[15px]";

const BODY_TEXT = { fontSize: "clamp(18px, 4vw, 26px)", fontWeight: 400, color: "#fff" } as const;

function CopyIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <rect x="3.5" y="3.5" width="8" height="8" rx="1.5" stroke="currentColor" />
      <path d="M8.5 1.5V1.5C8.5 0.95 8.05 0.5 7.5 0.5H2C1.17 0.5 0.5 1.17 0.5 2V7.5C0.5 8.05 0.95 8.5 1.5 8.5" stroke="currentColor" />
    </svg>
  );
}

export default function Hero() {
  const { displayed, done } = useTypewriter(TYPED_TEXT);
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShowActions(true), 400);
    return () => clearTimeout(t);
  }, []);

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(EMAIL);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard can be unavailable (insecure context, denied permission); the address stays visible.
    }
  };

  return (
    <section className="relative z-[1] flex h-screen flex-col justify-end overflow-hidden px-5 pb-12 sm:px-8 md:justify-center md:px-10 md:pb-0">
      <div className="relative z-10 max-w-xl">
        <p className="pointer-events-none mb-5 select-none sm:mb-6" style={{ ...BODY_TEXT, lineHeight: 1.3, filter: "blur(4px)" }}>
          Hey there, meet A.R.I.A,
          <br />
          Mainframe's Adaptive Response Interface Agent
        </p>

        <p className="mb-5 sm:mb-6" style={{ ...BODY_TEXT, lineHeight: 1.35, minHeight: 54 }} aria-label={TYPED_TEXT}>
          <span aria-hidden="true">{displayed}</span>
          {!done && (
            <span className="animate-blink ml-[2px] inline-block h-[1.1em] w-[2px] bg-white align-middle" aria-hidden="true" />
          )}
        </p>

        <div
          className="flex flex-wrap gap-y-1"
          style={{
            opacity: showActions ? 1 : 0,
            transform: showActions ? "translateY(0)" : "translateY(8px)",
            transition: "opacity 0.4s ease, transform 0.4s ease",
          }}
        >
          {ACTIONS.map(({ label, subject }) => (
            <a
              key={label}
              href={`mailto:${EMAIL}?subject=${encodeURIComponent(subject)}`}
              className={`${PILL} border-black/10 bg-white text-black hover:bg-black hover:text-white`}
            >
              {label}
            </a>
          ))}
          <button
            type="button"
            onClick={copyEmail}
            aria-label={`Copy email address ${EMAIL}`}
            className={`${PILL} gap-2 border-white bg-transparent text-white hover:bg-white hover:text-black sm:gap-3`}
          >
            <span>
              Reach us: <span className="underline underline-offset-1">{EMAIL}</span>
            </span>
            <CopyIcon />
          </button>
          <span className="sr-only" aria-live="polite">
            {copied ? "Email address copied" : ""}
          </span>
        </div>
      </div>
    </section>
  );
}
