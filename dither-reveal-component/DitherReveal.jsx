// Dither Reveal: text that scrambles through dither glyphs and locks into place
// character by character. A plain-React port of the Framer component
// https://framer.com/m/Dither-Reveal-LUnvnb.js (by Nora, https://x.com/SalXNura),
// with the same props, defaults and behaviour, minus the Framer-only APIs.

import { useEffect, useMemo, useRef, useState } from "react"

const CHARSETS = {
    dither: ["░", "▒", "▓", "█"],
    binary: ["0", "1"],
    blocks: ["▖", "▘", "▝", "▗", "▚", "▞", "▛", "▜", "▟", "▙"],
    noise: ["*", "#", "%", "+", "-", ".", "░", "▒"],
}

// Shrinks the IntersectionObserver zone to one band of the viewport.
const VIEWPORT_MARGIN = {
    top: "0px 0px -85% 0px",
    center: "-42.5% 0px -42.5% 0px",
    bottom: "-85% 0px 0px 0px",
}

// "final" -> real text, fully visible; "hidden" -> transparent, keeps layout.
const makeCells = (lines, mode) =>
    lines.map((line) =>
        line.split("").map((ch) => ({ ch, locked: mode === "final", hidden: mode === "hidden" }))
    )

// Fires once when the element enters the given rootMargin band.
function useInViewOnce(ref, rootMargin) {
    const [inView, setInView] = useState(false)
    useEffect(() => {
        const el = ref.current
        if (!el || inView) return
        if (typeof IntersectionObserver === "undefined") {
            setInView(true)
            return
        }
        const io = new IntersectionObserver(
            (entries) => {
                if (entries.some((e) => e.isIntersecting)) {
                    setInView(true)
                    io.disconnect()
                }
            },
            { rootMargin, threshold: 0 }
        )
        io.observe(el)
        return () => io.disconnect()
    }, [ref, rootMargin, inView])
    return inView
}

export default function DitherReveal(props) {
    const {
        text,
        font,
        textColor,
        scrambleColor,
        charset,
        customChars,
        swapSpeed,
        charRevealTime,
        staggerDelay,
        startDelay,
        revealDirection,
        trigger,
        scrollPosition,
        lineAlign,
        tag,
        style,
        className,
    } = { ...DitherReveal.defaultProps, ...props }

    const containerRef = useRef(null)
    const rafRef = useRef(null)
    const lastSwapRef = useRef(0)
    const [started, setStarted] = useState(false)

    // A literal "\n" typed into a single-line field also breaks the line.
    const lines = useMemo(() => text.replace(/\\n/g, "\n").split("\n"), [text])
    const [displayLines, setDisplayLines] = useState(() => makeCells(lines, "hidden"))
    const isInView = useInViewOnce(
        containerRef,
        VIEWPORT_MARGIN[scrollPosition] || VIEWPORT_MARGIN.center
    )

    const pool = useMemo(
        () =>
            charset === "custom" && customChars
                ? customChars.split("")
                : CHARSETS[charset] || CHARSETS.dither,
        [charset, customChars]
    )

    useEffect(() => {
        if (trigger === "mount") setStarted(true)
        else if (trigger === "inView" && isInView) setStarted(true)
    }, [trigger, isInView])

    // Reset to hidden when the text changes.
    useEffect(() => {
        setDisplayLines(makeCells(lines, "hidden"))
    }, [lines])

    useEffect(() => {
        if (!started) return
        // Show users who prefer reduced motion the final text straight away.
        if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
            setDisplayLines(makeCells(lines, "final"))
            return
        }
        lastSwapRef.current = -Infinity

        // One timeline across all lines, so stagger and order flow over line breaks.
        const flatChars = []
        lines.forEach((line, lineIndex) => {
            line.split("").forEach((ch, charIndex) => flatChars.push({ ch, lineIndex, charIndex }))
        })
        const len = flatChars.length
        if (len === 0) return

        let order = Array.from({ length: len }, (_, i) => i)
        if (revealDirection === "random") {
            order = order
                .map((v) => [Math.random(), v])
                .sort((a, b) => a[0] - b[0])
                .map((p) => p[1])
        } else if (revealDirection === "center") {
            const mid = (len - 1) / 2
            order = order.slice().sort((a, b) => Math.abs(a - mid) - Math.abs(b - mid))
        } else if (revealDirection === "right") {
            order = order.slice().reverse()
        }

        const lockAt = new Array(len).fill(0)
        order.forEach((flatIndex, revealPos) => {
            const s = startDelay * 1e3 + revealPos * staggerDelay * 1e3
            lockAt[flatIndex] = s + charRevealTime * 1e3
        })
        const swapMs = Math.max(16, swapSpeed * 1e3)
        const maxLock = Math.max(...lockAt)
        const randomGlyph = () => pool[Math.floor(Math.random() * pool.length)]

        let cancelled = false
        let animStart = null
        const tick = (now) => {
            if (cancelled) return
            if (animStart === null) animStart = now
            const elapsed = now - animStart
            if (elapsed - lastSwapRef.current >= swapMs) {
                lastSwapRef.current = elapsed
                const nextLines = lines.map((line) => new Array(line.length).fill(null))
                flatChars.forEach(({ ch, lineIndex, charIndex }, i) => {
                    let cell
                    if (ch === " ") cell = { ch: " ", locked: true, hidden: false }
                    else if (elapsed >= lockAt[i]) cell = { ch, locked: true, hidden: false }
                    else cell = { ch: randomGlyph(), locked: false, hidden: false }
                    nextLines[lineIndex][charIndex] = cell
                })
                setDisplayLines(nextLines)
            }
            if (elapsed < maxLock + swapMs) rafRef.current = requestAnimationFrame(tick)
            else setDisplayLines(makeCells(lines, "final"))
        }
        rafRef.current = requestAnimationFrame(tick)
        return () => {
            cancelled = true
            cancelAnimationFrame(rafRef.current)
        }
    }, [started, lines, swapSpeed, charRevealTime, staggerDelay, startDelay, revealDirection, pool])

    const Tag = tag || "div"
    return (
        <Tag
            ref={containerRef}
            className={className}
            aria-label={lines.join(" ")}
            style={{
                ...font,
                width: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems:
                    lineAlign === "left" ? "flex-start" : lineAlign === "right" ? "flex-end" : "center",
                textAlign: lineAlign,
                ...style,
            }}
        >
            {displayLines.map((line, li) => (
                <div key={li} aria-hidden="true" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {line.map((item, ci) => (
                        <span
                            key={ci}
                            style={{
                                color: item.hidden ? "transparent" : item.locked ? textColor : scrambleColor,
                            }}
                        >
                            {item.ch}
                        </span>
                    ))}
                    {line.length === 0 ? " " : null}
                </div>
            ))}
        </Tag>
    )
}

DitherReveal.defaultProps = {
    text: "First line of the reveal.\nSecond line appears right below it.",
    font: {
        fontSize: 32,
        fontWeight: 700,
        fontFamily: "Inter, system-ui, sans-serif",
        letterSpacing: "0px",
        lineHeight: "1.4em",
    },
    textColor: "#111111",
    scrambleColor: "#999999",
    charset: "dither", // "dither" | "binary" | "blocks" | "noise" | "custom"
    customChars: "",
    swapSpeed: 0.05, // seconds between glyph changes
    charRevealTime: 0.4, // seconds each character scrambles
    staggerDelay: 0.02, // seconds between characters
    startDelay: 0, // seconds after the trigger
    revealDirection: "left", // "left" | "right" | "center" | "random"
    trigger: "inView", // "inView" | "mount"
    scrollPosition: "center", // "top" | "center" | "bottom"
    lineAlign: "left", // "left" | "center" | "right"
    tag: "div",
}
