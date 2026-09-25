// Career tracks and catalog data for the DataCamp-style homepage

// ─── Career Tracks (DataCamp-style) ────────────────────────────────────────

export interface CareerTrackData {
  slug: string;
  title: string;
  description: string;
  icon: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  estimatedHours: number;
  courseCount: number;
  skills: string[];
}

export const careerTracks: CareerTrackData[] = [
  {
    slug: "full-stack",
    title: "Full Stack Developer",
    description:
      "Master both frontend and backend. Build complete web applications from database to UI.",
    icon: "layers",
    difficulty: "intermediate",
    estimatedHours: 120,
    courseCount: 12,
    skills: ["React", "Node.js", "PostgreSQL", "REST APIs", "Authentication"],
  },
  {
    slug: "backend-engineer",
    title: "Backend Engineer",
    description:
      "Design robust server-side systems. APIs, databases, authentication, and scalable architecture.",
    icon: "server",
    difficulty: "intermediate",
    estimatedHours: 100,
    courseCount: 10,
    skills: ["Python", "Django", "PostgreSQL", "Docker", "System Design"],
  },
  {
    slug: "frontend-dev",
    title: "Frontend Developer",
    description:
      "Craft beautiful, performant user interfaces. Master modern CSS, JavaScript, and React.",
    icon: "monitor",
    difficulty: "beginner",
    estimatedHours: 80,
    courseCount: 8,
    skills: ["HTML/CSS", "JavaScript", "React", "TypeScript", "Accessibility"],
  },
  {
    slug: "devops",
    title: "DevOps Engineer",
    description:
      "Automate deployments, manage infrastructure, and build CI/CD pipelines for reliable software delivery.",
    icon: "git-branch",
    difficulty: "advanced",
    estimatedHours: 90,
    courseCount: 7,
    skills: ["Docker", "CI/CD", "Linux", "Cloud", "Monitoring"],
  },
];

// ─── Catalog Projects (for catalog section) ────────────────────────────────

export interface CatalogItem {
  slug: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  category: string;
  estimatedHours: number;
  rating: number;
  learnerCount: number;
  type: "project" | "challenge";
}

export const catalogItems: CatalogItem[] = [
  {
    slug: "rest-api",
    title: "Build a REST API",
    description: "Build a RESTful API with proper routing, validation, and documentation.",
    difficulty: "beginner",
    category: "Backend",
    estimatedHours: 20,
    rating: 4.7,
    learnerCount: 3200,
    type: "project",
  },
  {
    slug: "portfolio-site",
    title: "Portfolio Website",
    description: "Design and build a responsive portfolio site with modern CSS and animations.",
    difficulty: "beginner",
    category: "Frontend",
    estimatedHours: 15,
    rating: 4.8,
    learnerCount: 5100,
    type: "project",
  },
  {
    slug: "url-shortener",
    title: "URL Shortener",
    description: "Design a URL shortening service with data modeling and redirect strategies.",
    difficulty: "intermediate",
    category: "Full Stack",
    estimatedHours: 30,
    rating: 4.6,
    learnerCount: 2100,
    type: "project",
  },
  {
    slug: "two-sum",
    title: "Two Sum Challenge",
    description: "Find two numbers that add up to a target. Optimize for time complexity.",
    difficulty: "beginner",
    category: "Algorithms",
    estimatedHours: 1,
    rating: 4.5,
    learnerCount: 8400,
    type: "challenge",
  },
  {
    slug: "real-time-chat",
    title: "Real-time Chat App",
    description: "Build a messaging app with WebSocket connections and room management.",
    difficulty: "advanced",
    category: "Full Stack",
    estimatedHours: 40,
    rating: 4.9,
    learnerCount: 1500,
    type: "project",
  },
  {
    slug: "docker-pipeline",
    title: "Docker CI/CD Pipeline",
    description: "Set up a complete CI/CD pipeline with Docker, GitHub Actions, and deployment.",
    difficulty: "advanced",
    category: "DevOps",
    estimatedHours: 25,
    rating: 4.7,
    learnerCount: 1800,
    type: "project",
  },
  {
    slug: "valid-parentheses",
    title: "Valid Parentheses",
    description: "Determine if a string of brackets is properly nested and balanced.",
    difficulty: "beginner",
    category: "Algorithms",
    estimatedHours: 1,
    rating: 4.4,
    learnerCount: 7200,
    type: "challenge",
  },
  {
    slug: "markdown-compiler",
    title: "Markdown Compiler",
    description: "Build a markdown-to-HTML compiler from scratch with AST parsing.",
    difficulty: "intermediate",
    category: "Frontend",
    estimatedHours: 25,
    rating: 4.8,
    learnerCount: 1200,
    type: "project",
  },
];

// ─── Testimonials ──────────────────────────────────────────────────────────

export interface Testimonial {
  name: string;
  role: string;
  avatar: string;
  quote: string;
  rating: number;
}

export const testimonials: Testimonial[] = [
  {
    name: "Aarav Sharma",
    role: "Junior Developer at TCS",
    avatar: "",
    quote:
      "Code-Yaar helped me go from tutorial hell to actually building things. I landed my first dev job after completing 3 projects here.",
    rating: 5,
  },
  {
    name: "Priya Patel",
    role: "CS Student",
    avatar: "",
    quote:
      "The project-based approach is exactly what I needed. Instead of just watching videos, I was building real applications from week one.",
    rating: 5,
  },
  {
    name: "Rahul Kumar",
    role: "Freelance Developer",
    avatar: "",
    quote:
      "The challenges sharpened my problem-solving skills. My confidence in interviews went through the roof after doing 50+ problems here.",
    rating: 5,
  },
];

// ─── Stats ─────────────────────────────────────────────────────────────────

export const stats = [
  { value: "10K+", label: "Learners" },
  { value: "50+", label: "Projects" },
  { value: "100+", label: "Challenges" },
  { value: "20+", label: "Skills" },
];

// ─── Catalog Categories ────────────────────────────────────────────────────

export const catalogCategories = [
  "All",
  "Frontend",
  "Backend",
  "Full Stack",
  "DevOps",
  "Algorithms",
];
