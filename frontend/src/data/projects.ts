import type { Project } from "@/types";

/**
 * Development-only demo fixtures.
 *
 * These describe *project definitions* (what could be built), not user
 * progress. They are shown only in development when the backend returns an
 * empty project library, and are clearly labelled as demo content in the UI.
 * The shape mirrors the Django `ProjectSerializer` contract so real API data
 * drops in without changes.
 */
export const demoProjects: Project[] = [
  {
    id: 1,
    slug: "rest-api",
    title: "REST API",
    description:
      "Build a RESTful API with proper routing, validation, error handling, and documentation.",
    difficulty: "beginner",
    technologies: ["Python", "FastAPI", "SQLite"],
    estimated_hours: 20,
    milestones: [
      { id: 1, title: "Project Setup", description: "Initialize project", order: 1 },
      { id: 2, title: "Data Model", description: "Define data models", order: 2 },
      { id: 3, title: "CRUD Endpoints", description: "Implement CRUD operations", order: 3 },
      { id: 4, title: "Validation", description: "Add input validation", order: 4 },
      { id: 5, title: "Documentation", description: "Write API docs", order: 5 },
    ],
  },
  {
    id: 2,
    slug: "url-shortener",
    title: "URL Shortener",
    description:
      "Design and build a URL shortening service. Consider data modeling, hashing, and redirect strategies.",
    difficulty: "intermediate",
    technologies: ["TypeScript", "Node.js", "PostgreSQL"],
    estimated_hours: 30,
    milestones: [
      { id: 1, title: "Architecture", description: "Plan system architecture", order: 1 },
      { id: 2, title: "Database", description: "Set up database schema", order: 2 },
      { id: 3, title: "Shortening Logic", description: "Implement encoding/decoding", order: 3 },
      { id: 4, title: "API Layer", description: "Build API endpoints", order: 4 },
      { id: 5, title: "Analytics", description: "Track clicks", order: 5 },
    ],
  },
  {
    id: 3,
    slug: "task-orchestrator",
    title: "Task Orchestrator",
    description:
      "Build a distributed task scheduling system with priority queues, retries, and monitoring.",
    difficulty: "advanced",
    technologies: ["Go", "Redis", "gRPC"],
    estimated_hours: 50,
    milestones: [
      { id: 1, title: "Core Engine", description: "Build execution engine", order: 1 },
      { id: 2, title: "Priority Queue", description: "Implement scheduling", order: 2 },
      { id: 3, title: "Retry Logic", description: "Add backoff strategies", order: 3 },
      { id: 4, title: "Monitoring", description: "Build dashboard", order: 4 },
    ],
  },
  {
    id: 4,
    slug: "markdown-compiler",
    title: "Markdown Compiler",
    description:
      "Build a markdown-to-HTML compiler from scratch. Parse syntax trees and produce clean output.",
    difficulty: "intermediate",
    technologies: ["TypeScript", "AST"],
    estimated_hours: 25,
    milestones: [
      { id: 1, title: "Tokenizer", description: "Build lexical tokenizer", order: 1 },
      { id: 2, title: "Parser", description: "Create AST parser", order: 2 },
      { id: 3, title: "Renderer", description: "Implement HTML rendering", order: 3 },
      { id: 4, title: "Extensions", description: "Add custom syntax", order: 4 },
    ],
  },
  {
    id: 5,
    slug: "cli-toolkit",
    title: "CLI Toolkit",
    description:
      "Create a command-line tool with subcommands, flags, interactive prompts, and colored output.",
    difficulty: "beginner",
    technologies: ["Python", "Click"],
    estimated_hours: 15,
    milestones: [
      { id: 1, title: "Command Structure", description: "Define commands", order: 1 },
      { id: 2, title: "Input Handling", description: "Handle flags and args", order: 2 },
      { id: 3, title: "Output Formatting", description: "Add colored output", order: 3 },
    ],
  },
  {
    id: 6,
    slug: "real-time-chat",
    title: "Real-time Chat",
    description:
      "Build a real-time messaging app with WebSocket connections, room management, and persistence.",
    difficulty: "advanced",
    technologies: ["TypeScript", "WebSocket", "PostgreSQL"],
    estimated_hours: 40,
    milestones: [
      { id: 1, title: "Connection Layer", description: "Set up WebSocket server", order: 1 },
      { id: 2, title: "Room System", description: "Implement rooms", order: 2 },
      { id: 3, title: "Message Protocol", description: "Design message format", order: 3 },
      { id: 4, title: "Persistence", description: "Store message history", order: 4 },
    ],
  },
];
