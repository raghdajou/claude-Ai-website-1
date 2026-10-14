import { fadeIn } from "./fadeIn";

function DotGrid({ size = 3, className = "" }: { size?: number; className?: string }) {
  return (
    <span className={`grid gap-[3px] ${className}`} style={{ gridTemplateColumns: `repeat(${size}, 4px)` }} aria-hidden="true">
      {Array.from({ length: size * size }, (_, i) => (
        <span key={i} className="h-1 w-1 rounded-full bg-current" />
      ))}
    </span>
  );
}

export default function Logos() {
  return (
    <div
      className="animate-fade-in-up mt-24 flex flex-wrap items-center justify-center gap-x-12 gap-y-8 text-gray-400"
      style={fadeIn(0.8)}
      aria-label="Trusted by"
    >
      <span className="text-lg font-bold tracking-[0.25em]">INTERSCOPE</span>
      <span className="text-xl font-bold tracking-wide">SPOTIFY</span>
      <span className="flex items-center gap-2 text-xl font-semibold">
        <DotGrid />
        Nexera
      </span>
      <span className="font-serif text-3xl italic">M3</span>
      <span className="flex items-center gap-2 text-sm font-semibold tracking-[0.2em]">
        <span className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-current text-[11px] tracking-normal">
          LC
        </span>
        LAURA COLE
      </span>
      <span className="flex items-center gap-1.5 text-xl font-medium">
        <span className="flex gap-[3px]" aria-hidden="true">
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
        </span>
        vertex
      </span>
    </div>
  );
}
