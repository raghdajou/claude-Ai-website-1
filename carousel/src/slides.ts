export type Slide = {
  title: string;
  category: string;
  description: string;
  image: string;
  alt: string;
  buttonText: string;
  link: string;
};

// Photos: Unsplash (https://unsplash.com/license) — Warren Umoh, Sangharsh Lohakare, MJH SHIKDER, Braňo.
export const SLIDES: Slide[] = [
  {
    title: "Code of life.",
    category: "Art direction",
    description: "A closer look at the structure that shapes every living thing.",
    image: "images/dna-1.jpg",
    alt: "White and blue DNA double helix on a dark background",
    buttonText: "Explore project",
    link: "#",
  },
  {
    title: "Pure signal.",
    category: "Visual identity",
    description: "Light, glow and a single strand — reduced to what matters.",
    image: "images/dna-5.jpg",
    alt: "Glowing white DNA double helix",
    buttonText: "View project",
    link: "#",
  },
  {
    title: "Built from particles.",
    category: "Creative exploration",
    description: "Thousands of tiny points come together to form something whole.",
    image: "images/dna-7.jpg",
    alt: "DNA helix made of red and white particles",
    buttonText: "Discover more",
    link: "#",
  },
  {
    title: "Deep blue.",
    category: "Selected work",
    description: "Calm colour, sharp detail, and a form everyone recognises.",
    image: "images/dna-10.jpg",
    alt: "DNA double helix render on blue",
    buttonText: "Take a look",
    link: "#",
  },
];
