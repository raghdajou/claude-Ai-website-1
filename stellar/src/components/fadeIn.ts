import type { CSSProperties } from "react";

// Pairs with .animate-fade-in-up: start hidden, let the animation fill to visible.
export const fadeIn = (delay: number): CSSProperties => ({ opacity: 0, animationDelay: `${delay}s` });
