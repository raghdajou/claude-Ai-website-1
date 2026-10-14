import { useEffect, useLayoutEffect, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";
import { SLIDES, type Slide } from "./slides";

const ACCENT = "#D9FF85";
const EASE = "cubic-bezier(0.22, 1, 0.36, 1)";
const DURATION = 0.8; // seconds
const SWIPE_THRESHOLD = 36; // px

function Arrow({ left = false }: { left?: boolean }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true" className={left ? "rotate-180" : ""}>
      <path d="M4 12h15M13 6l6 6-6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  useEffect(() => {
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

const pad = (n: number) => String(n).padStart(2, "0");

export default function CinemaCarousel({ slides = SLIDES, startSlide = 1 }: { slides?: Slide[]; startSlide?: number }) {
  const count = slides.length;
  const [active, setActive] = useState(Math.min(Math.max(startSlide - 1, 0), count - 1));
  const [width, setWidth] = useState(1200);
  const rootRef = useRef<HTMLDivElement>(null);
  const gesture = useRef<{ x: number; y: number; id: number; horizontal: boolean } | null>(null);
  const suppressClickUntil = useRef(0);
  const reducedMotion = usePrefersReducedMotion();

  useLayoutEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const measure = () => el.clientWidth > 0 && setWidth(el.clientWidth);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Layout: the active slide takes the remaining width; the others collapse into strips.
  const mobile = width < 640;
  const compact = width < 900;
  const inset = mobile ? 12 : 24;
  const innerWidth = Math.max(1, width - inset * 2);
  const gap = count <= 1 ? 0 : Math.min(mobile ? 6 : 10, (innerWidth * 0.08) / (count - 1));
  const stripWidth = count <= 1 ? 0 : Math.min(mobile ? 12 : 92, (innerWidth * (mobile ? 0.2 : 0.42)) / (count - 1));
  const expandedWidth = Math.max(1, innerWidth - (count - 1) * (stripWidth + gap));
  const contentPadding = mobile ? 20 : compact ? 28 : 42;
  const showStripLabels = !mobile && stripWidth >= 38;

  const t = (seconds: number, delay = 0) =>
    reducedMotion ? "none" : `${seconds}s ${EASE} ${delay}s`;

  const goTo = (index: number) => setActive(Math.min(Math.max(index, 0), count - 1));
  const step = (dir: number) => setActive((i) => (i + dir + count) % count);

  const onKeyDown = (e: KeyboardEvent) => {
    const keys: Record<string, () => void> = {
      ArrowRight: () => step(1),
      ArrowLeft: () => step(-1),
      Home: () => goTo(0),
      End: () => goTo(count - 1),
    };
    if (keys[e.key]) {
      e.preventDefault();
      keys[e.key]();
    }
  };

  // Horizontal swipe changes slide; vertical movement is left to page scrolling.
  const onPointerDown = (e: PointerEvent) => {
    if (count <= 1 || !e.isPrimary || e.button !== 0) return;
    gesture.current = { x: e.clientX, y: e.clientY, id: e.pointerId, horizontal: false };
  };
  const onPointerMove = (e: PointerEvent) => {
    const g = gesture.current;
    if (!g || g.id !== e.pointerId) return;
    const dx = e.clientX - g.x;
    const dy = e.clientY - g.y;
    if (!g.horizontal && Math.abs(dy) > 12 && Math.abs(dy) > Math.abs(dx)) {
      gesture.current = null;
      return;
    }
    if (!g.horizontal && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) {
      g.horizontal = true;
      e.currentTarget.setPointerCapture(e.pointerId);
    }
    if (g.horizontal) suppressClickUntil.current = Date.now() + 300;
  };
  const onPointerUp = (e: PointerEvent) => {
    const g = gesture.current;
    gesture.current = null;
    if (!g || g.id !== e.pointerId) return;
    const dx = e.clientX - g.x;
    if (g.horizontal && Math.abs(dx) > SWIPE_THRESHOLD) step(dx < 0 ? 1 : -1);
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId);
  };

  return (
    <div
      ref={rootRef}
      role="region"
      aria-roledescription="carousel"
      aria-label="Selected projects"
      onKeyDown={onKeyDown}
      className="flex h-full w-full min-w-0 flex-col overflow-hidden bg-[#141414] text-white"
      style={{ padding: inset }}
    >
      <div
        className="flex min-h-0 w-full flex-1 touch-pan-y"
        style={{ gap }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={() => (gesture.current = null)}
        onClickCapture={(e) => {
          if (Date.now() < suppressClickUntil.current) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
      >
        {slides.map((slide, index) => {
          const isActive = index === active;
          return (
            <div
              key={slide.title}
              role="group"
              aria-roledescription="slide"
              aria-label={`${index + 1} of ${count}: ${slide.title}`}
              className="relative isolate h-full min-w-0 shrink-0 overflow-hidden bg-[#292929]"
              style={{
                width: isActive ? expandedWidth : stripWidth,
                borderRadius: mobile ? 14 : 20,
                transition: `width ${t(DURATION)}`,
              }}
            >
              {/* Image stays full-size and slides behind the strip, so it reveals rather than squashes. */}
              <div
                className="absolute inset-y-0 left-0"
                style={{
                  width: expandedWidth,
                  transform: isActive ? "none" : `translateX(${-expandedWidth * 0.12}px) scale(1.08)`,
                  transition: `transform ${t(DURATION)}`,
                }}
              >
                <img
                  src={slide.image}
                  alt={slide.alt}
                  draggable={false}
                  className="pointer-events-none block h-full w-full select-none object-cover"
                />
              </div>
              <div
                className="pointer-events-none absolute inset-0"
                style={{
                  background:
                    "linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0) 32%, rgba(0,0,0,0.33) 62%, rgba(0,0,0,0.78) 100%)",
                }}
              />
              <div
                className="pointer-events-none absolute inset-0 bg-black"
                style={{ opacity: isActive ? 0 : 0.35, transition: `opacity ${t(DURATION)}` }}
              />

              {/* Active content */}
              <a
                href={isActive ? slide.link : undefined}
                tabIndex={isActive ? 0 : -1}
                aria-hidden={!isActive}
                draggable={false}
                className="absolute inset-y-0 left-0 flex flex-col justify-between text-white no-underline focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-[5px]"
                style={{
                  width: expandedWidth,
                  padding: contentPadding,
                  borderRadius: "inherit",
                  outlineColor: ACCENT,
                  pointerEvents: isActive ? "auto" : "none",
                  opacity: isActive ? 1 : 0,
                  transform: isActive || reducedMotion ? "none" : "translateY(12px)",
                  transition: isActive
                    ? `opacity ${t(DURATION * 0.55, DURATION * 0.18)}, transform ${t(DURATION * 0.55, DURATION * 0.18)}`
                    : `opacity ${t(DURATION * 0.3)}, transform ${t(DURATION * 0.3)}`,
                }}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.1em]">
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: ACCENT }} />
                    {slide.category}
                  </span>
                  <span className="text-xs tabular-nums opacity-75">{pad(index + 1)}</span>
                </div>
                <div className="max-w-[650px] pt-10">
                  <h2
                    className="m-0 font-medium [overflow-wrap:anywhere] [text-wrap:balance]"
                    style={{ fontSize: mobile ? 38 : compact ? 52 : 76, lineHeight: 0.98, letterSpacing: "-0.055em" }}
                  >
                    {slide.title}
                  </h2>
                  <p className="mt-[18px] max-w-[340px] leading-[1.55] opacity-80" style={{ fontSize: mobile ? 13 : 14 }}>
                    {slide.description}
                  </p>
                  <span className="group mt-6 inline-flex items-center gap-[18px] py-1 text-xs font-medium">
                    {slide.buttonText}
                    <span
                      className="grid h-9 w-9 shrink-0 place-items-center rounded-full text-[#141414] transition-transform duration-300 group-hover:translate-x-1 motion-reduce:transition-none"
                      style={{ background: ACCENT }}
                    >
                      <Arrow />
                    </span>
                  </span>
                </div>
              </a>

              {/* Collapsed strip label */}
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 flex flex-col items-center justify-between py-6"
                style={{
                  opacity: !isActive && showStripLabels ? 1 : 0,
                  transition: `opacity ${t(DURATION * 0.3)}`,
                }}
              >
                <span className="text-[11px] tabular-nums opacity-70">{pad(index + 1)}</span>
                <span className="max-h-[70%] overflow-hidden text-ellipsis whitespace-nowrap text-base font-medium tracking-[-0.02em] [transform:rotate(180deg)] [writing-mode:vertical-rl]">
                  {slide.title}
                </span>
              </div>

              {!isActive && (
                <button
                  type="button"
                  aria-label={`Show ${slide.title}`}
                  onClick={() => goTo(index)}
                  className="absolute inset-0 h-full w-full cursor-pointer border-0 bg-transparent p-0 focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-[5px]"
                  style={{ borderRadius: "inherit", outlineColor: ACCENT }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Footer: counter, progress segments, prev/next */}
      <div className="flex shrink-0 items-center justify-between gap-5" style={{ paddingTop: mobile ? 16 : 22 }}>
        <div className="flex min-w-0 flex-1 items-center" style={{ gap: mobile ? 12 : 22 }}>
          <span className="whitespace-nowrap text-[11px] tabular-nums tracking-[0.05em]">
            {pad(active + 1)}
            <span className="opacity-35"> / {pad(count)}</span>
          </span>
          <div className="flex max-w-full items-center gap-[5px]" style={{ width: mobile ? 100 : 180 }}>
            {slides.map((slide, index) => (
              <button
                key={slide.title}
                type="button"
                aria-label={`Go to ${slide.title}`}
                aria-current={index === active ? "true" : undefined}
                onClick={() => goTo(index)}
                className="flex h-8 min-w-0 flex-1 cursor-pointer items-center border-0 bg-transparent p-0"
              >
                <span
                  className="block h-0.5 w-full rounded-sm"
                  style={{
                    background: index === active ? ACCENT : "#fff",
                    opacity: index === active ? 1 : 0.2,
                    transition: `opacity ${t(DURATION)}, background-color ${t(DURATION)}`,
                  }}
                />
              </button>
            ))}
          </div>
        </div>
        {count > 1 && (
          <div className="flex gap-2">
            {[
              { label: "Previous slide", dir: -1 },
              { label: "Next slide", dir: 1 },
            ].map(({ label, dir }) => (
              <button
                key={label}
                type="button"
                aria-label={label}
                onClick={() => step(dir)}
                className="inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full border border-white/20 bg-transparent text-white transition-[background-color,transform] duration-200 hover:bg-white/10 active:scale-95 focus-visible:outline focus-visible:outline-2"
                style={{ outlineColor: ACCENT }}
              >
                <Arrow left={dir < 0} />
              </button>
            ))}
          </div>
        )}
      </div>

      <span className="sr-only" aria-live="polite" aria-atomic="true">
        {active + 1} of {count}: {slides[active].title}
      </span>
    </div>
  );
}
