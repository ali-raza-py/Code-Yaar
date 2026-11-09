"""Seed the Code Yaar course ecosystem with comprehensive curriculum data.

Usage:
    python manage.py seed_course_ecosystem
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from learning.models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Project, ProjectMilestone, Achievement,
)


TRACKS = [
    {
        "slug": "computer-science-foundations",
        "title": "Computer Science Foundations",
        "description": "Build a rock-solid foundation in computer science. From computational thinking to software engineering, master the concepts that power every modern application.",
        "category": "programming",
        "difficulty": "beginner",
        "estimated_hours": 200,
        "learning_objectives": [
            "Understand how computers process information",
            "Apply computational thinking to real problems",
            "Design efficient algorithms and data structures",
            "Write clean, maintainable object-oriented code",
            "Work with databases, operating systems, and networks",
            "Follow software engineering best practices",
        ],
        "order": 1,
        "courses": [
            ("Introduction to Computer Science", "beginner", 20, "python", "What computers are, how they work, and why software matters. Your first step into the world of computing.", ["No prior experience needed"]),
            ("Computational Thinking and Problem Solving", "beginner", 25, "python", "Learn to break down problems, identify patterns, and design step-by-step solutions.", ["Basic computer literacy"]),
            ("Data Structures and Algorithms", "intermediate", 40, "python", "Master arrays, linked lists, trees, graphs, sorting, and searching. The core of technical interviews.", ["Python basics", "Basic mathematics"]),
            ("Object-Oriented Programming", "intermediate", 30, "python", "Classes, objects, inheritance, polymorphism, encapsulation, and design patterns.", ["Python basics"]),
            ("Database Fundamentals", "beginner", 25, "python", "Relational databases, SQL, normalization, and data modeling.", ["Basic computer literacy"]),
            ("Operating Systems Fundamentals", "intermediate", 30, "python", "Processes, threads, memory management, file systems, and concurrency.", ["Basic computer literacy"]),
            ("Computer Networks", "intermediate", 30, "python", "TCP/IP, HTTP, DNS, routing, and network security basics.", ["Basic computer literacy"]),
            ("Software Engineering Principles", "intermediate", 35, "python", "SDLC, testing, version control, code review, and clean code.", ["Basic programming experience"]),
        ],
    },
    {
        "slug": "ai-machine-learning",
        "title": "Artificial Intelligence & Machine Learning",
        "description": "From mathematics to production AI systems. Build real machine learning models, train neural networks, and create intelligent applications.",
        "category": "ai",
        "difficulty": "intermediate",
        "estimated_hours": 350,
        "learning_objectives": [
            "Understand the mathematics behind machine learning",
            "Build and train ML models with scikit-learn",
            "Design neural networks with TensorFlow/PyTorch",
            "Process natural language with NLP techniques",
            "Build AI agents and agentic systems",
            "Deploy AI applications to production",
        ],
        "order": 2,
        "courses": [
            ("Mathematics for Machine Learning", "beginner", 40, "python", "Linear algebra, calculus, and optimization — the math that powers AI.", ["High school math"]),
            ("Statistics and Probability for Data Science", "beginner", 35, "python", "Distributions, hypothesis testing, Bayesian thinking, and statistical inference.", ["Basic math"]),
            ("Data Analysis with Python", "beginner", 30, "python", "Explore, clean, and analyze real datasets with Python.", ["Python basics"]),
            ("NumPy and Pandas", "beginner", 30, "python", "Master the two most important Python libraries for data science.", ["Python basics"]),
            ("Data Visualization", "beginner", 25, "python", "Create compelling charts and dashboards with Matplotlib, Seaborn, and Plotly.", ["Python basics"]),
            ("Machine Learning Fundamentals", "intermediate", 40, "python", "Supervised learning, model evaluation, feature engineering, and the ML workflow.", ["Python", "Basic statistics"]),
            ("Supervised and Unsupervised Learning", "intermediate", 40, "python", "Classification, regression, clustering, dimensionality reduction, and ensemble methods.", ["ML fundamentals"]),
            ("Neural Networks and Deep Learning", "advanced", 50, "python", "Build neural networks from scratch, train CNNs, RNNs, and transformers.", ["ML fundamentals", "Linear algebra"]),
            ("Natural Language Processing", "advanced", 40, "python", "Tokenization, embeddings, sentiment analysis, and text generation.", ["Python", "ML basics"]),
            ("Generative AI and Large Language Models", "advanced", 45, "python", "Understand LLMs, prompt engineering, RAG, and fine-tuning.", ["NLP basics", "Python"]),
            ("AI Application Development", "advanced", 35, "python", "Build production AI apps with APIs, vector databases, and deployment.", ["LLM basics", "Backend basics"]),
            ("AI Agents and Agentic Systems", "advanced", 40, "python", "Tool use, memory, planning, multi-agent systems, and autonomous workflows.", ["AI app development"]),
        ],
    },
    {
        "slug": "backend-software-development",
        "title": "Backend & Software Development",
        "description": "Design, build, and deploy production-grade backend systems. From REST APIs to microservices architecture.",
        "category": "web",
        "difficulty": "intermediate",
        "estimated_hours": 300,
        "learning_objectives": [
            "Design and build RESTful APIs",
            "Implement authentication and authorization",
            "Design efficient database schemas",
            "Build background job systems",
            "Write comprehensive backend tests",
            "Apply software architecture patterns",
        ],
        "order": 3,
        "courses": [
            ("REST API Development", "beginner", 25, "python", "HTTP, REST principles, resource design, status codes, and API versioning.", ["Basic programming"]),
            ("Django Backend Engineering", "intermediate", 45, "python", "Build full-featured web applications with Django, ORM, and the admin panel.", ["Python basics", "HTTP basics"]),
            ("FastAPI Development", "intermediate", 35, "python", "High-performance async APIs with FastAPI, Pydantic, and automatic docs.", ["Python basics", "REST basics"]),
            ("Authentication and Authorization", "intermediate", 30, "python", "JWT, OAuth2, session auth, RBAC, and security best practices.", ["Backend basics"]),
            ("PostgreSQL and Database Design", "intermediate", 35, "python", "Schema design, indexing, query optimization, and database migrations.", ["SQL basics"]),
            ("Redis and Caching", "intermediate", 25, "python", "In-memory data stores, caching strategies, pub/sub, and session management.", ["Backend basics"]),
            ("Background Jobs and Task Queues", "intermediate", 30, "python", "Celery, task queues, scheduled jobs, and async processing patterns.", ["Backend basics", "Redis"]),
            ("API Security", "advanced", 30, "python", "Rate limiting, input validation, CORS, CSRF, and OWASP API Top 10.", ["REST API experience"]),
            ("Backend Testing", "intermediate", 30, "python", "Unit tests, integration tests, API tests, mocking, and CI integration.", ["Backend basics"]),
            ("Software Architecture and Design Patterns", "advanced", 40, "python", "Clean architecture, SOLID, microservices, and event-driven design.", ["Backend experience"]),
        ],
    },
    {
        "slug": "frontend-engineering",
        "title": "Frontend Engineering",
        "description": "Build modern, accessible, performant user interfaces. From HTML to production React/Next.js applications.",
        "category": "web",
        "difficulty": "beginner",
        "estimated_hours": 280,
        "learning_objectives": [
            "Build semantic, accessible HTML pages",
            "Create responsive layouts with modern CSS",
            "Master JavaScript and TypeScript",
            "Build interactive UIs with React",
            "Deploy production Next.js applications",
            "Optimize frontend performance",
        ],
        "order": 4,
        "courses": [
            ("HTML and Web Fundamentals", "beginner", 20, "javascript", "Semantic HTML, accessibility basics, forms, and media.", ["None"]),
            ("CSS Architecture and Responsive Design", "beginner", 30, "javascript", "Flexbox, Grid, responsive design, CSS variables, and architecture patterns.", ["HTML basics"]),
            ("JavaScript Programming", "beginner", 40, "javascript", "Variables, functions, DOM, events, async/await, and ES6+ features.", ["HTML/CSS basics"]),
            ("TypeScript", "intermediate", 30, "javascript", "Type system, interfaces, generics, and type-safe development.", ["JavaScript basics"]),
            ("React Development", "intermediate", 45, "javascript", "Components, hooks, state, effects, routing, and data fetching.", ["JavaScript basics"]),
            ("Next.js Engineering", "advanced", 40, "javascript", "Server components, routing, data fetching, and deployment.", ["React basics"]),
            ("State Management", "intermediate", 25, "javascript", "Redux, Zustand, Context API, and server state with React Query.", ["React basics"]),
            ("Frontend Performance Optimization", "advanced", 25, "javascript", "Core Web Vitals, bundle optimization, lazy loading, and caching.", ["React experience"]),
            ("Accessibility and UI Engineering", "intermediate", 25, "javascript", "ARIA, keyboard navigation, screen readers, and inclusive design.", ["HTML/CSS basics"]),
            ("Production Frontend Projects", "advanced", 35, "javascript", "Build and deploy real-world frontend applications.", ["React/Next.js experience"]),
        ],
    },
    {
        "slug": "cybersecurity-systems",
        "title": "Cybersecurity & Systems",
        "description": "Defend systems, networks, and applications. Learn offensive and defensive security in ethical, authorized contexts.",
        "category": "other",
        "difficulty": "intermediate",
        "estimated_hours": 260,
        "learning_objectives": [
            "Understand security fundamentals and threat models",
            "Secure web applications against OWASP Top 10",
            "Implement cryptography and secure coding",
            "Analyze security incidents and forensics",
            "Operate security monitoring systems",
            "Secure cloud infrastructure",
        ],
        "order": 5,
        "courses": [
            ("Cybersecurity Fundamentals", "beginner", 25, "other", "Security principles, threat modeling, and the CIA triad.", ["Basic computer literacy"]),
            ("Linux and Command Line", "beginner", 30, "other", "Terminal, file system, permissions, and shell scripting.", ["Basic computer literacy"]),
            ("Networking Fundamentals", "beginner", 30, "other", "TCP/IP, HTTP, DNS, firewalls, and network topology.", ["Basic computer literacy"]),
            ("Web Application Security", "intermediate", 35, "other", "OWASP Top 10, XSS, SQL injection, CSRF, and secure headers.", ["Web development basics", "HTTP basics"]),
            ("Secure Coding Practices", "intermediate", 30, "other", "Input validation, output encoding, authentication, and secure APIs.", ["Programming basics"]),
            ("Cryptography Fundamentals", "intermediate", 30, "other", "Symmetric/asymmetric encryption, hashing, PKI, and TLS.", ["Basic math", "Networking basics"]),
            ("Digital Forensics Fundamentals", "advanced", 35, "other", "Evidence collection, disk analysis, memory forensics, and incident response.", ["Linux basics", "Security basics"]),
            ("Security Operations and Incident Response", "advanced", 35, "other", "SIEM, log analysis, threat hunting, and incident management.", ["Security basics", "Networking"]),
            ("Cloud Security Fundamentals", "intermediate", 30, "other", "IAM, network security, data protection, and compliance in cloud.", ["Cloud basics", "Security basics"]),
        ],
    },
    {
        "slug": "cloud-devops-infrastructure",
        "title": "Cloud, DevOps & Infrastructure",
        "description": "Automate, deploy, and scale applications. From containerization to cloud infrastructure and CI/CD pipelines.",
        "category": "other",
        "difficulty": "intermediate",
        "estimated_hours": 280,
        "learning_objectives": [
            "Use Git and GitHub for professional workflows",
            "Containerize applications with Docker",
            "Build CI/CD pipelines",
            "Deploy to cloud platforms (AWS, GCP)",
            "Manage infrastructure as code",
            "Monitor and operate production systems",
        ],
        "order": 6,
        "courses": [
            ("Git and GitHub Workflows", "beginner", 30, "other", "Version control, branching, pull requests, and collaboration.", ["Basic computer literacy"]),
            ("Linux Administration", "intermediate", 35, "other", "System administration, user management, networking, and automation.", ["Linux basics"]),
            ("Docker and Containerization", "intermediate", 30, "other", "Containers, images, Docker Compose, and container orchestration.", ["Linux basics"]),
            ("CI/CD Fundamentals", "intermediate", 25, "other", "Continuous integration, delivery, and deployment pipelines.", ["Git basics"]),
            ("Cloud Computing Fundamentals", "beginner", 25, "other", "IaaS, PaaS, SaaS, cloud models, and provider comparison.", ["Basic computer literacy"]),
            ("AWS Cloud Foundations", "intermediate", 40, "other", "EC2, S3, RDS, Lambda, IAM, and VPC on AWS.", ["Cloud basics"]),
            ("Google Cloud Foundations", "intermediate", 35, "other", "Compute Engine, Cloud Storage, BigQuery, and GKE on GCP.", ["Cloud basics"]),
            ("Infrastructure as Code", "advanced", 30, "other", "Terraform, CloudFormation, and declarative infrastructure management.", ["Cloud basics", "Linux"]),
            ("Monitoring and Logging", "intermediate", 25, "other", "Prometheus, Grafana, ELK stack, and observability principles.", ["Linux basics", "Cloud basics"]),
            ("Deployment and Production Operations", "advanced", 35, "other", "Zero-downtime deployments, rollback, scaling, and incident management.", ["Docker", "CI/CD", "Cloud"]),
        ],
    },
    {
        "slug": "data-engineering",
        "title": "Data Engineering",
        "description": "Build the infrastructure that powers data-driven organizations. From SQL to distributed data pipelines.",
        "category": "ai",
        "difficulty": "intermediate",
        "estimated_hours": 220,
        "learning_objectives": [
            "Design and query relational databases",
            "Build ETL pipelines",
            "Process large datasets with Spark",
            "Design data warehouses",
            "Orchestrate data workflows",
            "Ensure data quality and reliability",
        ],
        "order": 7,
        "courses": [
            ("Data Engineering Foundations", "beginner", 25, "python", "What data engineering is, the data lifecycle, and the modern data stack.", ["Basic programming"]),
            ("SQL for Data Professionals", "beginner", 30, "python", "Advanced SQL: joins, window functions, CTEs, and query optimization.", ["Basic SQL"]),
            ("Advanced PostgreSQL", "intermediate", 35, "python", "Advanced features, performance tuning, replication, and administration.", ["SQL basics", "PostgreSQL basics"]),
            ("Data Pipelines and ETL", "intermediate", 35, "python", "Build extract-transform-load pipelines with Python and modern tools.", ["Python", "SQL"]),
            ("Apache Spark Fundamentals", "intermediate", 35, "python", "Distributed data processing with PySpark and Spark SQL.", ["Python", "Data pipelines"]),
            ("Data Warehousing", "intermediate", 30, "python", "Dimensional modeling, star schemas, and warehouse design.", ["SQL", "Data pipelines"]),
            ("Workflow Orchestration", "intermediate", 25, "python", "Airflow, DAGs, scheduling, and pipeline monitoring.", ["Data pipelines"]),
            ("Data Quality and Reliability", "advanced", 25, "python", "Testing, validation, monitoring, and data contracts.", ["Data pipelines", "SQL"]),
        ],
    },
    {
        "slug": "mobile-application-development",
        "title": "Mobile & Application Development",
        "description": "Build native and cross-platform mobile applications. From fundamentals to production deployment.",
        "category": "web",
        "difficulty": "intermediate",
        "estimated_hours": 200,
        "learning_objectives": [
            "Understand mobile development fundamentals",
            "Build cross-platform apps with Flutter/Dart",
            "Develop React Native applications",
            "Design mobile UI architectures",
            "Integrate APIs and manage state",
            "Test and deploy mobile apps",
        ],
        "order": 8,
        "courses": [
            ("Mobile Development Fundamentals", "beginner", 20, "javascript", "Mobile platforms, UI patterns, and the mobile development lifecycle.", ["Basic programming"]),
            ("Flutter and Dart", "intermediate", 40, "javascript", "Build beautiful cross-platform apps with Flutter and Dart.", ["OOP basics"]),
            ("React Native", "intermediate", 40, "javascript", "Build native mobile apps with React and JavaScript.", ["React basics"]),
            ("Mobile UI Architecture", "intermediate", 25, "javascript", "Navigation, layouts, animations, and responsive mobile design.", ["Mobile basics"]),
            ("API Integration", "intermediate", 25, "javascript", "REST APIs, authentication, caching, and offline support in mobile apps.", ["Mobile basics", "API basics"]),
            ("Local Storage and State Management", "intermediate", 25, "javascript", "SQLite, AsyncStorage, and state management patterns for mobile.", ["Mobile basics"]),
            ("Mobile Testing and Deployment", "advanced", 25, "javascript", "Unit tests, E2E tests, app store submission, and CI/CD for mobile.", ["Mobile development experience"]),
        ],
    },
]

CHAPTERS = [
    ("Introduction and Foundations", "Get started with the key concepts and what you will learn."),
    ("Core Concepts", "Deep dive into the fundamental ideas and techniques."),
    ("Practical Application", "Apply what you have learned through hands-on exercises."),
    ("Advanced Topics", "Explore deeper and more complex aspects."),
    ("Assessment and Projects", "Test your knowledge and build portfolio projects."),
]

LESSON_TITLES = [
    "Welcome and Overview",
    "Key Concepts Explained",
    "Deep Dive: Core Principles",
    "Hands-On Practice",
    "Building Your First Project",
    "Advanced Techniques",
    "Module Assessment",
    "Course Capstone Project",
]

EXERCISE_DEFS = [
    ("Knowledge Check", "multiple_choice", "easy", 10, [
        {"id": "a", "text": "Option A", "is_correct": True},
        {"id": "b", "text": "Option B", "is_correct": False},
        {"id": "c", "text": "Option C", "is_correct": False},
        {"id": "d", "text": "Option D", "is_correct": False},
    ]),
    ("Code Practice", "code", "medium", 25, []),
    ("Debugging Challenge", "debugging", "hard", 40, []),
]


def _lang(language):
    return {"python": "python", "javascript": "javascript", "cpp": "cpp", "java": "java"}.get(language, "python")


class Command(BaseCommand):
    help = "Seed the Code Yaar course ecosystem."

    def handle(self, *args, **options):
        # Clean partial data from previous timed-out run
        self.stdout.write("Cleaning partial seed data...")
        # Delete only the new tracks (not existing ones)
        new_slugs = [t["slug"] for t in TRACKS]
        CareerTrack.objects.filter(slug__in=new_slugs).delete()

        self.stdout.write("Seeding tracks and courses...")
        for track_data in TRACKS:
            track, _ = CareerTrack.objects.get_or_create(
                slug=track_data["slug"],
                defaults={
                    "title": track_data["title"],
                    "description": track_data["description"],
                    "category": track_data["category"],
                    "difficulty": track_data["difficulty"],
                    "estimated_hours": track_data["estimated_hours"],
                    "learning_objectives": track_data["learning_objectives"],
                    "order": track_data["order"],
                    "is_active": True,
                    "is_published": True,
                },
            )

            for course_idx, (title, difficulty, hours, language, description, prereqs) in enumerate(track_data["courses"], 1):
                course_slug = slugify(title)
                course, created = Course.objects.get_or_create(
                    slug=course_slug,
                    defaults={
                        "title": title,
                        "subtitle": f"Part of {track.title}",
                        "description": description,
                        "track": track,
                        "difficulty": difficulty,
                        "language": language,
                        "manual_estimated_hours": hours,
                        "prerequisites": ", ".join(prereqs),
                        "learning_objectives": [
                            f"Understand the core concepts of {title}",
                            f"Apply {title} principles in practice",
                            f"Build projects using {title} skills",
                        ],
                        "is_active": True,
                        "is_published": True,
                        "is_free": True,
                        "order": course_idx,
                        "tags": [track_data["slug"], difficulty, language],
                    },
                )
                if created:
                    self._seed_course(course, language, difficulty, hours)

            self.stdout.write(f"  Track done: {track.title}")

        self.stdout.write(self.style.SUCCESS("Done."))

    def _seed_course(self, course, language, difficulty, hours):
        lang = _lang(language)
        chapters_to_create = []
        for ch_idx, (ch_title, ch_desc) in enumerate(CHAPTERS, 1):
            chapters_to_create.append(Chapter(
                course=course,
                slug=slugify(ch_title),
                title=ch_title,
                description=ch_desc,
                order=ch_idx,
                xp_reward=500,
                is_active=True,
            ))
        Chapter.objects.bulk_create(chapters_to_create, ignore_conflicts=True)
        chapters = list(Chapter.objects.filter(course=course).order_by("order"))

        lessons_to_create = []
        for ch_idx, chapter in enumerate(chapters, 1):
            lesson_count = 4 if ch_idx <= 3 else 3
            for les_idx in range(1, lesson_count + 1):
                if ch_idx == 1 and les_idx == 1:
                    lt = f"Welcome to {course.title}"
                elif ch_idx == 1 and les_idx == 2:
                    lt = f"What You Will Learn in {course.title}"
                elif ch_idx == 2 and les_idx == 1:
                    lt = "Core Concepts Explained"
                elif ch_idx == 2 and les_idx == 2:
                    lt = "Deep Dive: Key Principles"
                elif ch_idx == 3 and les_idx == 1:
                    lt = "Hands-On Practice"
                elif ch_idx == 3 and les_idx == 2:
                    lt = "Building Your First Project"
                elif ch_idx == 4 and les_idx == 1:
                    lt = "Advanced Techniques"
                elif ch_idx == 5 and les_idx == 1:
                    lt = "Module Assessment"
                elif ch_idx == 5 and les_idx == 2:
                    lt = "Course Capstone Project"
                else:
                    lt = f"{chapter.title} — Lesson {les_idx}"

                objective = f"Understand and apply {lt.lower()} in {course.title}."
                content = f"""## {lt}

### Learning Objective
{objective}

### Introduction
This lesson introduces {lt.lower()} as part of {course.title}. You will learn the essential concepts and practice them through exercises.

### Key Concepts
- Key concept 1 of {lt}
- Key concept 2 of {lt}
- Key concept 3 of {lt}
- Practical application of {lt.lower()}

### Example
```{lang}
# Example: {lt}
print('Hello from {course.title}!')
```

### Common Mistakes
- Forgetting to follow the syntax rules
- Not testing edge cases
- Skipping the practice exercises

### Practice
Complete the exercises below to reinforce your understanding of {lt.lower()}.

### Summary
You have learned about {lt.lower()} in {course.title}. Review the key points and complete the exercises.
"""
                lessons_to_create.append(Lesson(
                    chapter=chapter,
                    slug=slugify(lt),
                    title=lt,
                    content_type="text",
                    learning_objective=objective,
                    content_body=content,
                    order=les_idx,
                    duration_minutes=25,
                    xp_reward=50,
                    is_active=True,
                    is_required=True,
                ))
        Lesson.objects.bulk_create(lessons_to_create, ignore_conflicts=True)
        lessons = list(Lesson.objects.filter(chapter__course=course).order_by("chapter__order", "order"))

        exercises_to_create = []
        for lesson in lessons:
            for ex_idx, (ex_title, ex_type, ex_diff, ex_xp, choices) in enumerate(EXERCISE_DEFS, 1):
                exercises_to_create.append(Exercise(
                    lesson=lesson,
                    slug=slugify(f"{lesson.title}-{ex_title}"),
                    title=f"{ex_title}: {lesson.title}",
                    exercise_type=ex_type,
                    instructions=f"Complete this {ex_type.replace('_', ' ')} exercise about {lesson.title.lower()}.",
                    context=f"This exercise reinforces your understanding of {lesson.title.lower()}.",
                    difficulty=ex_diff,
                    language=language if language in ("python", "javascript", "cpp", "java") else "python",
                    choices=choices,
                    starter_code=f"# Write your solution here\n# Topic: {lesson.title}\n" if ex_type in ("code", "debugging") else "",
                    solution_code=f"# Solution for {lesson.title}\nprint('Solution')\n" if ex_type in ("code", "debugging") else "",
                    test_cases=[{"input": "", "expected_output": "Solution"}] if ex_type in ("code", "debugging") else [],
                    xp_reward=ex_xp,
                    order=ex_idx,
                    is_active=True,
                ))
        Exercise.objects.bulk_create(exercises_to_create, ignore_conflicts=True)

        # Project
        project, _ = Project.objects.get_or_create(
            slug=slugify(f"{course.title}-capstone"),
            defaults={
                "title": f"{course.title} Capstone Project",
                "description": f"Build a real-world project applying everything you learned in {course.title}.",
                "difficulty": difficulty,
                "technologies": [language, "git"],
                "estimated_hours": max(5, hours // 4),
                "track": course.track,
                "is_active": True,
            },
        )
        milestones = [
            ("Planning", "Define requirements and design the architecture."),
            ("Implementation", "Build the core functionality."),
            ("Testing", "Write tests and fix bugs."),
            ("Deployment", "Deploy and document the project."),
        ]
        for ms_idx, (ms_title, ms_desc) in enumerate(milestones, 1):
            ProjectMilestone.objects.get_or_create(
                project=project, order=ms_idx,
                defaults={"title": ms_title, "description": ms_desc},
            )

        # Achievement
        Achievement.objects.get_or_create(
            slug=slugify(f"complete-{course.title}"),
            defaults={
                "title": f"{course.title} Graduate",
                "description": f"Completed all lessons and assessments in {course.title}.",
                "category": "course",
                "difficulty": "beginner" if difficulty in ("beginner", "elementary") else "intermediate" if difficulty == "intermediate" else "advanced",
                "xp_bonus": 200,
                "condition_type": "course_complete",
                "condition_value": course.slug,
                "is_active": True,
            },
        )
