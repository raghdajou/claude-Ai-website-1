import { Fragment, useEffect, useState } from "react";
import {
  Aperture,
  ArrowUpRight,
  Box,
  Brush,
  Camera,
  Chrome,
  Figma,
  Framer,
  Layers,
  Palette,
  PenTool,
  Sparkle,
  Type,
  Wand2,
  type LucideIcon,
} from "lucide-react";

const VIDEOS = {
  background:
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260507_150203_44a5bd32-516a-47ce-a077-8acbf9aa8991.mp4",
  raised:
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260507_154543_d5b83fc1-9cea-44f3-b5e8-8f325935211a.mp4",
  software:
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260507_153148_d7a3e1dd-e5d0-4ce6-8306-00d7522ecc44.mp4",
};

const TIMELINE = [
  { years: "2023-Now", role: "Freelance Creative", company: "Solo Studio" },
  { years: "2020-2023", role: "Head of Brand Design", company: "Rove Studio" },
  { years: "2017-2020", role: "Visual Stylist", company: "Ember Works" },
];

const ROW_ONE: LucideIcon[] = [Figma, Framer, Palette, PenTool, Layers, Type, Aperture, Chrome];
const ROW_TWO: LucideIcon[] = [Camera, Brush, Box, Wand2, Figma, Framer, Type, Layers];
const SOFTWARE = "Figma, Framer, Chrome, and tools for color, illustration, type, photography and 3D";

// Visible keyboard focus for links on the dark background.
const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0a]";

function usePrefersReducedMotion() {
  const query = "(prefers-reduced-motion: reduce)";
  const [reduced, setReduced] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

function SectionLabel({ children, align = "center" }: { children: string; align?: "center" | "start" }) {
  return (
    <div
      className={`flex items-center gap-2 text-xs uppercase tracking-[0.22em] text-white/75 ${
        align === "center" ? "justify-center" : "justify-start"
      }`}
    >
      <Sparkle className="h-3 w-3" strokeWidth={1.5} />
      <span>{children}</span>
      <Sparkle className="h-3 w-3" strokeWidth={1.5} />
    </div>
  );
}

function BackgroundVideo({ src }: { src: string }) {
  // With reduced motion, show the first frame instead of looping playback.
  const reducedMotion = usePrefersReducedMotion();
  return (
    <video
      key={reducedMotion ? "still" : "playing"}
      className="absolute inset-0 h-full w-full object-cover"
      src={src}
      autoPlay={!reducedMotion}
      loop
      muted
      playsInline
      preload={reducedMotion ? "metadata" : "auto"}
      aria-hidden="true"
    />
  );
}

function MarqueeRow({ icons, direction }: { icons: LucideIcon[]; direction: "left" | "right" }) {
  // Rendered twice so translating by -50% loops seamlessly.
  const items = [...icons, ...icons];
  return (
    <div className="marquee overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_8%,black_92%,transparent)]">
      <div
        className={`flex w-max gap-3 ${
          direction === "left" ? "animate-marquee-left" : "animate-marquee-right"
        }`}
      >
        {items.map((Icon, i) => (
          <div
            key={i}
            className="liquid-glass flex h-14 w-14 shrink-0 items-center justify-center rounded-xl md:h-16 md:w-16"
          >
            <Icon className="h-6 w-6 text-white/90" strokeWidth={1.5} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Features() {
  return (
    <section className="flex min-h-screen flex-col bg-[#0a0a0a] px-4 py-6 font-sans text-white antialiased sm:px-6 sm:py-8 md:px-10 md:py-10 lg:h-screen lg:px-14">
      {/* Header */}
      <header className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-3xl">
          <h1 className="text-[28px] font-normal leading-[1.15] tracking-tight sm:text-3xl md:text-4xl lg:text-[44px]">
            Hi, I'm Max Reed!
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-[1.6] text-white/60 md:text-[15px]">
            A London-based independent creator shaping sharp visual systems, web-ready products, and
            story-first campaigns. With a decade of craft behind me, I help ideas move with focus and
            intention.
          </p>
        </div>
        <a
          href="mailto:hi@maxreed.com"
          className={`liquid-glass inline-flex min-h-11 shrink-0 items-center self-start rounded-full px-5 py-2.5 text-sm text-white transition-colors hover:bg-white/5 sm:px-6 sm:py-3 ${FOCUS_RING}`}
        >
          Let's Team Up Today
        </a>
      </header>

      {/* Grid */}
      <div className="mt-6 grid flex-1 grid-cols-1 gap-4 md:mt-8 md:grid-cols-2 md:gap-5 lg:min-h-0 lg:grid-cols-3">
        {/* Column 1 — Background */}
        <article className="relative flex min-h-[420px] flex-col justify-between overflow-hidden rounded-2xl bg-black p-5 md:p-6 lg:min-h-0">
          <BackgroundVideo src={VIDEOS.background} />
          <div className="relative">
            <SectionLabel>Background</SectionLabel>
          </div>
          <div className="relative grid grid-cols-[auto_auto_1fr_auto] items-center gap-x-3 gap-y-3 text-[13px]">
            {TIMELINE.map((item) => (
              <Fragment key={item.years}>
                <span className="whitespace-nowrap text-white/70">{item.years}</span>
                <Sparkle className="h-3 w-3 text-white/60" strokeWidth={1.5} />
                <span className="text-white">{item.role}</span>
                <span className="text-right text-white/60">{item.company}</span>
              </Fragment>
            ))}
          </div>
        </article>

        {/* Column 2 — Client voice + 10M+ */}
        <div className="grid gap-4 md:grid-rows-[auto_1fr] md:gap-5 lg:min-h-0">
          <article className="noise-overlay relative overflow-hidden rounded-2xl bg-[#324444] p-5 md:p-6">
            <SectionLabel align="start">Client Voice</SectionLabel>
            <blockquote className="mt-4 text-[13px] leading-[1.6] text-white/85 sm:text-[13.5px]">
              “Max reshaped our image with a degree of finesse and vision that surpassed what we'd
              hoped for. The process felt graceful, and the outcomes speak for themselves.”
            </blockquote>
            <p className="mt-4 text-[13px] text-white/70">
              <span className="font-semibold text-white">Elena Brooks</span>, Creative Director — Halcyon
            </p>
          </article>

          <article className="relative flex min-h-[280px] flex-col items-center justify-center overflow-hidden rounded-2xl bg-black p-5 md:p-6 lg:min-h-0">
            <BackgroundVideo src={VIDEOS.raised} />
            <span className="relative text-5xl font-light tracking-tight drop-shadow-[0_4px_24px_rgba(0,0,0,0.45)] sm:text-6xl md:text-7xl lg:text-[88px]">
              10M+
            </span>
            <p className="absolute inset-x-0 bottom-5 text-center text-sm text-white/85 md:bottom-6">
              Raised for startups
            </p>
          </article>
        </div>

        {/* Column 3 — Daily software + Reach me */}
        <div className="grid gap-4 md:col-span-2 md:grid-cols-2 md:gap-5 lg:col-span-1 lg:min-h-0 lg:grid-cols-1 lg:grid-rows-[1fr_auto]">
          <article className="relative flex min-h-[300px] flex-col justify-between overflow-hidden rounded-2xl bg-black py-5 md:py-6 lg:min-h-0">
            <BackgroundVideo src={VIDEOS.software} />
            <div className="relative px-5 md:px-6">
              <SectionLabel>Daily Software</SectionLabel>
            </div>
            <p className="sr-only">Tools I use daily: {SOFTWARE}.</p>
            <div className="relative flex flex-col gap-3" aria-hidden="true">
              <MarqueeRow icons={ROW_ONE} direction="left" />
              <MarqueeRow icons={ROW_TWO} direction="right" />
            </div>
          </article>

          <article className="noise-overlay relative overflow-hidden rounded-2xl bg-[#324444] p-5 md:p-6">
            <SectionLabel align="start">Reach Me</SectionLabel>
            <div className="mt-3 text-[15px]">
              <a
                href="mailto:hi@maxreed.com"
                className={`block w-fit rounded py-1 text-white transition-colors hover:text-white/80 ${FOCUS_RING}`}
              >
                hi@maxreed.com
              </a>
              <a
                href="tel:+442078163"
                className={`block w-fit rounded py-1 text-white/75 transition-colors hover:text-white ${FOCUS_RING}`}
              >
                +44 207 81 63
              </a>
            </div>
            {/* Wrapper holds the position: .liquid-glass sets position: relative on itself. */}
            <div className="absolute right-5 top-5 z-10 md:right-6 md:top-6">
              <a
                href="mailto:hi@maxreed.com"
                aria-label="Email Max Reed"
                className={`liquid-glass flex h-11 w-11 items-center justify-center rounded-full transition-colors hover:bg-white/10 ${FOCUS_RING}`}
              >
                <ArrowUpRight className="h-4 w-4" strokeWidth={1.5} />
              </a>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
