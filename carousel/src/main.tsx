import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import CinemaCarousel from "./CinemaCarousel";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <main className="h-screen min-h-[560px]">
      <CinemaCarousel />
    </main>
  </StrictMode>,
);
