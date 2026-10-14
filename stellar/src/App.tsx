import Hero from "./components/Hero";
import Navbar from "./components/Navbar";

export default function App() {
  return (
    <div className="mx-auto max-w-7xl bg-white">
      <Navbar />
      <Hero />
    </div>
  );
}
