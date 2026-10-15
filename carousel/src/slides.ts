export type Slide = {
  title: string;
  category: string;
  description: string;
  image: string;
  alt: string;
  /** CSS object-position: which part of the photo stays in view when it's cropped */
  focus?: string;
  buttonText: string;
  link: string;
};

export const SLIDES: Slide[] = [
  {
    title: "Slow afternoons.",
    category: "Lifestyle",
    description: "Friends, sunlight and nowhere else to be — the kind of moment that feels like summer.",
    image: "images/picnic.jpg",
    alt: "Four friends lying on a cream blanket on the grass, laughing and looking up",
    focus: "50% 48%",
    buttonText: "View story",
    link: "#",
  },
  {
    title: "Look up.",
    category: "Nature study",
    description: "A ground-level view of the garden, where every blade of grass reaches for the sky.",
    image: "images/garden.jpg",
    alt: "Low-angle view of tall green grass and purple irises against a blue sky and trees",
    focus: "50% 42%",
    buttonText: "See the series",
    link: "#",
  },
];
