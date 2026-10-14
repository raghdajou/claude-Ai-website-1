import { BarChart3, BookOpen, Rocket, Star, Users, type LucideIcon } from "lucide-react";
import { Fragment, useEffect, useState } from "react";
import { fadeIn } from "./fadeIn";
import Logos from "./Logos";
import Overlay, { type TabId } from "./Overlays";

const VIDEO_SRC =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260319_165750_358b1e72-c921-48b7-aaac-f200994f32fb.mp4";

const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: "analyse", label: "Analyse", icon: BarChart3 },
  { id: "train", label: "Train", icon: BookOpen },
  { id: "testing", label: "Testing", icon: Users },
  { id: "deploy", label: "Deploy", icon: Rocket },
];

const CYCLE_MS = 4000;

function TabButton({ id, label, icon: Icon, active, onSelect }: (typeof TABS)[number] & { active: boolean; onSelect: (id: TabId) => void }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(id)}
      aria-pressed={active}
      className={`flex min-h-10 items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black ${
        active ? "bg-white text-black shadow-sm" : "text-gray-600 hover:text-black"
      }`}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {label}
    </button>
  );
}

export default function Hero() {
  const [activeTab, setActiveTab] = useState<TabId>("analyse");
  // Auto-cycling pauses while the pointer or keyboard focus is on the tabs or video.
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    // Re-created whenever the tab changes, so a manual pick gets a full 4s before moving on.
    const id = setInterval(() => {
      setActiveTab((current) => {
        const i = TABS.findIndex((t) => t.id === current);
        return TABS[(i + 1) % TABS.length].id;
      });
    }, CYCLE_MS);
    return () => clearInterval(id);
  }, [activeTab, paused]);

  const pauseHandlers = {
    onMouseEnter: () => setPaused(true),
    onMouseLeave: () => setPaused(false),
    onFocus: () => setPaused(true),
    onBlur: () => setPaused(false),
  };

  return (
    <section className="mx-auto max-w-7xl px-6 pb-32 pt-24 text-center">
      <div className="animate-fade-in-up mb-8 inline-flex items-center gap-2" style={fadeIn(0.2)}>
        <span className="flex h-6 w-6 items-center justify-center rounded border border-gray-300">
          <Star className="h-3.5 w-3.5 fill-black" aria-hidden="true" />
        </span>
        <span className="text-sm font-medium text-black">4.9 rating from 18.3K+ users</span>
      </div>

      <h1
        className="animate-fade-in-up mb-5 text-6xl font-normal leading-[1.1] tracking-tight md:text-7xl lg:text-[80px]"
        style={fadeIn(0.3)}
      >
        Work Smarter. Move Faster.
        <br />
        <span className="bg-gradient-to-r from-black via-gray-500 to-gray-400 bg-clip-text text-transparent">
          AI Powers You Up.
        </span>
      </h1>

      <p className="animate-fade-in-up mx-auto mb-8 max-w-2xl text-lg text-gray-600 md:text-xl" style={fadeIn(0.4)}>
        Intelligent automation syncs with the tools you love to streamline tasks, boost output, and save time.
      </p>

      <div className="animate-fade-in-up" style={fadeIn(0.5)}>
        <button
          type="button"
          className="mb-12 rounded-full bg-black px-8 py-3 text-base font-medium text-white transition-colors hover:bg-gray-800"
        >
          Begin Free Trial
        </button>
      </div>

      <div {...pauseHandlers}>
        <div className="animate-fade-in-up mb-6 flex justify-center" style={fadeIn(0.6)}>
          <div className="rounded-lg bg-gray-100 p-1" role="group" aria-label="Product stages">
            <div className="grid grid-cols-2 gap-1 md:hidden">
              {TABS.map((tab) => (
                <TabButton key={tab.id} {...tab} active={activeTab === tab.id} onSelect={setActiveTab} />
              ))}
            </div>
            <div className="hidden items-center md:flex">
              {TABS.map((tab, i) => (
                <Fragment key={tab.id}>
                  {i > 0 && <span className="mx-1 h-5 w-px bg-gray-300" aria-hidden="true" />}
                  <TabButton {...tab} active={activeTab === tab.id} onSelect={setActiveTab} />
                </Fragment>
              ))}
            </div>
          </div>
        </div>

        <div className="animate-fade-in-up" style={fadeIn(0.7)}>
          <div className="relative h-[400px] overflow-hidden rounded-3xl md:h-[500px]">
            <video src={VIDEO_SRC} autoPlay loop muted playsInline aria-hidden="true" className="h-full w-full object-cover" />
            <Overlay key={activeTab} tab={activeTab} />
          </div>
        </div>
      </div>

      <Logos />
    </section>
  );
}
