import { useEffect, useRef } from "react";

const VIDEO_SRC =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260826_041744_63efcd78-bf7d-4039-99e2-2461e8a61903.mp4";

// Fraction of the video's duration covered by dragging the mouse across the full window width.
const SENSITIVITY = 0.8;

export default function BackgroundVideo() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let prevX: number | null = null;
    let targetTime = 0;
    let seeking = false;

    // Only one seek in flight at a time; onSeeked picks up wherever the target moved to.
    const seek = () => {
      if (Math.abs(video.currentTime - targetTime) < 0.001) return;
      seeking = true;
      video.currentTime = targetTime;
    };

    const onMouseMove = (e: MouseEvent) => {
      const currentX = e.clientX;
      if (prevX === null) {
        prevX = currentX;
        return;
      }
      const delta = currentX - prevX;
      prevX = currentX;

      const duration = video.duration;
      if (!Number.isFinite(duration) || duration <= 0) return;

      const offset = (delta / window.innerWidth) * SENSITIVITY * duration;
      targetTime = Math.min(Math.max(targetTime + offset, 0), duration);
      if (!seeking) seek();
    };

    const onSeeked = () => {
      seeking = false;
      seek();
    };

    window.addEventListener("mousemove", onMouseMove);
    video.addEventListener("seeked", onSeeked);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      video.removeEventListener("seeked", onSeeked);
    };
  }, []);

  return (
    <video
      ref={videoRef}
      src={VIDEO_SRC}
      muted
      playsInline
      preload="auto"
      aria-hidden="true"
      className="fixed inset-0 z-0 h-full w-full object-cover"
      style={{ objectPosition: "70% center" }}
    />
  );
}
