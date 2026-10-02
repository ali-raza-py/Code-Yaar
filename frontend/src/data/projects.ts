import type { Project } from "@/types";

export const demoProjects: Project[] = [
  {
    id: "1",
    slug: "rest-api",
    title: "REST API",
    description:
      "Build a RESTful API with proper routing, validation, error handling, and documentation.",
    difficulty: "beginner",
    technologies: ["Python", "FastAPI", "SQLite"],
    estimatedHours: 20,
    skillsDeveloped: ["API Design", "HTTP Methods", "Data Validation", "Error Handling"],
    milestones: [
      { id: "m1", title: "Project Setup", description: "Initialize project", completed: true },
      { id: "m2", title: "Data Model", description: "Define data models", completed: true },
      { id: "m3", title: "CRUD Endpoints", description: "Implement CRUD operations", completed: false },
      { id: "m4", title: "Validation", description: "Add input validation", completed: false },
      { id: "m5", title: "Documentation", description: "Write API docs", completed: false },
    ],
    status: "available",
  },
  {
    id: "2",
    slug: "url-shortener",
    title: "URL Shortener",
    description:
      "Design and build a URL shortening service. Consider data modeling, hashing, and redirect strategies.",
    difficulty: "intermediate",
    technologies: ["TypeScript", "Node.js", "PostgreSQL"],
    estimatedHours: 30,
    skillsDeveloped: ["System Design", "Database Modeling", "Hashing", "Caching"],
    milestones: [
      { id: "m1", title: "Architecture", description: "Plan system architecture", completed: true },
      { id: "m2", title: "Database", description: "Set up database schema", completed: true },
      { id: "m3", title: "Shortening Logic", description: "Implement encoding/decoding", completed: true },
      { id: "m4", title: "API Layer", description: "Build API endpoints", completed: false },
      { id: "m5", title: "Analytics", description: "Track clicks", completed: false },
    ],
    status: "available",
  },
  {
    id: "3",
    slug: "task-orchestrator",
    title: "Task Orchestrator",
    description:
      "Build a distributed task scheduling system with priority queues, retries, and monitoring.",
    difficulty: "advanced",
    technologies: ["Go", "Redis", "gRPC"],
    estimatedHours: 50,
    skillsDeveloped: ["Concurrency", "Distributed Systems", "Queue Design", "Fault Tolerance"],
    milestones: [
      { id: "m1", title: "Core Engine", description: "Build execution engine", completed: false },
      { id: "m2", title: "Priority Queue", description: "Implement scheduling", completed: false },
      { id: "m3", title: "Retry Logic", description: "Add backoff strategies", completed: false },
      { id: "m4", title: "Monitoring", description: "Build dashboard", completed: false },
    ],
    status: "available",
  },
  {
    id: "4",
    slug: "markdown-compiler",
    title: "Markdown Compiler",
    description:
      "Build a markdown-to-HTML compiler from scratch. Parse syntax trees and produce clean output.",
    difficulty: "intermediate",
    technologies: ["TypeScript", "AST"],
    estimatedHours: 25,
    skillsDeveloped: ["Parsing", "AST Design", "Compiler Theory", "Testing"],
    milestones: [
      { id: "m1", title: "Tokenizer", description: "Build lexical tokenizer", completed: false },
      { id: "m2", title: "Parser", description: "Create AST parser", completed: false },
      { id: "m3", title: "Renderer", description: "Implement HTML rendering", completed: false },
      { id: "m4", title: "Extensions", description: "Add custom syntax", completed: false },
    ],
    status: "available",
  },
  {
    id: "5",
    slug: "cli-toolkit",
    title: "CLI Toolkit",
    description:
      "Create a command-line tool with subcommands, flags, interactive prompts, and colored output.",
    difficulty: "beginner",
    technologies: ["Python", "Click"],
    estimatedHours: 15,
    skillsDeveloped: ["CLI Design", "Argument Parsing", "Terminal UI", "Packaging"],
    milestones: [
      { id: "m1", title: "Command Structure", description: "Define commands", completed: false },
      { id: "m2", title: "Input Handling", description: "Handle flags and args", completed: false },
      { id: "m3", title: "Output Formatting", description: "Add colored output", completed: false },
    ],
    status: "available",
  },
  {
    id: "6",
    slug: "real-time-chat",
    title: "Real-time Chat",
    description:
      "Build a real-time messaging app with WebSocket connections, room management, and persistence.",
    difficulty: "advanced",
    technologies: ["TypeScript", "WebSocket", "PostgreSQL"],
    estimatedHours: 40,
    skillsDeveloped: ["WebSockets", "Real-time Systems", "State Management", "Authentication"],
    milestones: [
      { id: "m1", title: "Connection Layer", description: "Set up WebSocket server", completed: false },
      { id: "m2", title: "Room System", description: "Implement rooms", completed: false },
      { id: "m3", title: "Message Protocol", description: "Design message format", completed: false },
      { id: "m4", title: "Persistence", description: "Store message history", completed: false },
    ],
    status: "available",
  },
];

export function getProjectBySlug(slug: string): Project | undefined {
  return demoProjects.find((p) => p.slug === slug);
}
