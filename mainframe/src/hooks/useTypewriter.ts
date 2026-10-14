import { useEffect, useState } from "react";

// Reveals `text` one character at a time after `startDelay` ms.
export function useTypewriter(text: string, speed = 38, startDelay = 600) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(0);
    let interval: ReturnType<typeof setInterval> | undefined;
    const timeout = setTimeout(() => {
      interval = setInterval(() => {
        setCount((n) => {
          if (n + 1 >= text.length && interval) clearInterval(interval);
          return Math.min(n + 1, text.length);
        });
      }, speed);
    }, startDelay);

    return () => {
      clearTimeout(timeout);
      if (interval) clearInterval(interval);
    };
  }, [text, speed, startDelay]);

  return { displayed: text.slice(0, count), done: count >= text.length };
}
