import { ChevronDown, Star } from "lucide-react";
import { fadeIn } from "./fadeIn";

const LINKS = [
  { label: "Solutions", menu: true },
  { label: "For Teams", menu: true },
  { label: "About Us", menu: false },
  { label: "Learn Hub", menu: false },
];

export default function Navbar() {
  return (
    <nav
      className="animate-fade-in-up mx-auto flex max-w-7xl items-center justify-between px-6 py-4"
      style={fadeIn(0.1)}
    >
      <a href="/" className="flex items-center gap-2">
        <Star className="h-5 w-5 fill-black" aria-hidden="true" />
        <span className="text-lg font-semibold">Stellar.ai</span>
      </a>

      <div className="hidden items-center gap-8 md:flex">
        {LINKS.map(({ label, menu }) => (
          <a key={label} href="#" className="flex items-center gap-1 text-sm text-gray-700 hover:text-black">
            {label}
            {menu && <ChevronDown className="h-4 w-4" aria-hidden="true" />}
          </a>
        ))}
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <a href="#" className="text-sm text-gray-700 hover:text-black">
          Login
        </a>
        <button
          type="button"
          className="rounded-full bg-black px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-gray-800"
        >
          Get started free
        </button>
      </div>
    </nav>
  );
}
