export type Slide = {
  title: string;
  category: string;
  description: string;
  image: string;
  alt: string;
  buttonText: string;
  link: string;
};

// Photos and text from the Framer "Modern Carousel" component's defaults.
export const SLIDES: Slide[] = [
  {
    title: "Beyond ordinary.",
    category: "Art direction",
    description: "A different perspective on the shapes, colours and details around us.",
    image: "images/slide-1.jpg",
    alt: "A single pink flower spike against a soft blue and violet background",
    buttonText: "Explore project",
    link: "#",
  },
  {
    title: "Soft encounters.",
    category: "Visual identity",
    description: "Organic forms meet a clear visual language. Made to feel a little different.",
    image: "images/slide-2.jpg",
    alt: "A round purple allium flower on a pink and lavender background",
    buttonText: "View project",
    link: "#",
  },
  {
    title: "New dimensions.",
    category: "Creative exploration",
    description: "An exploration of depth, movement and unexpected combinations.",
    image: "images/slide-3.jpg",
    alt: "A thin flower stem silhouetted against a glowing orange background",
    buttonText: "Discover more",
    link: "#",
  },
  {
    title: "In good shape.",
    category: "Selected work",
    description: "Simple ideas brought to life through thoughtful design and playful details.",
    image: "images/slide-4.jpg",
    alt: "A dried flower head silhouetted against a bright yellow background",
    buttonText: "Take a look",
    link: "#",
  },
];
