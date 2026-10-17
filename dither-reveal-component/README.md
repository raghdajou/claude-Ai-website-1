# Dither Reveal

Text that scrambles through dither glyphs (░▒▓█) and locks into place character by character.
Built from the Framer component https://framer.com/m/Dither-Reveal-LUnvnb.js by Nora (https://x.com/SalXNura).

- `DitherReveal.framer.js`: the original Framer code component, unchanged. Paste it into a Framer code file.
- `DitherReveal.jsx`: the same component for any React project (no Framer dependency), same props and defaults.
- `index.html`: demo of the component with its default props on a 1400 x 788 Behance artboard.

```jsx
import DitherReveal from "./DitherReveal"

<DitherReveal
  text={"First line of the reveal.\nSecond line appears right below it."}
  font={{ fontFamily: "Inter", fontSize: 32, fontWeight: 700, lineHeight: "1.4em" }}
  textColor="#111111"
  scrambleColor="#999999"
  charset="dither"          // dither | binary | blocks | noise | custom
  revealDirection="left"    // left | right | center | random
  trigger="inView"          // inView | mount
/>
```

Timing props, all in seconds: `startDelay` (0), `staggerDelay` (0.02), `charRevealTime` (0.4), `swapSpeed` (0.05).
