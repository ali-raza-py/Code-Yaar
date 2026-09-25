import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Check, Circle, Clock, Wrench } from "lucide-react";
import { demoProjects } from "@/data/projects";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const project = demoProjects.find((p) => p.slug === slug);
  if (!project) return { title: "Project Not Found" };
  return { title: project.title, description: project.description };
}

export async function generateStaticParams() {
  return demoProjects.map((p) => ({ slug: p.slug }));
}

export default async function ProjectDetailPage({ params }: Props) {
  const { slug } = await params;
  const project = demoProjects.find((p) => p.slug === slug);
  if (!project) notFound();
  const completedMilestones = project.milestones.filter((m) => m.completed).length;
  const progress = completedMilestones / project.milestones.length;
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
      <Link href="/projects" className="mb-8 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to Projects
      </Link>
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="outline" className={project.difficulty === "beginner" ? "bg-accent/10 text-accent" : project.difficulty === "intermediate" ? "bg-primary/10 text-primary" : "bg-destructive/10 text-destructive"}>
            {project.difficulty}
          </Badge>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" /> {project.estimatedHours}h
          </div>
        </div>
        <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{project.title}</h1>
        <p className="mt-4 text-muted-foreground">{project.description}</p>
      </div>
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-mono font-medium">{Math.round(progress * 100)}%</span>
          </div>
          <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-secondary">
            <div className="h-full bg-primary" style={{ width: `${progress * 100}%` }} />
          </div>
        </CardContent>
      </Card>
      <div className="grid gap-8 md:grid-cols-3">
        <div className="md:col-span-2">
          <h2 className="mb-4 text-lg font-semibold">Milestones</h2>
          <div className="space-y-3">
            {project.milestones.map((milestone, i) => (
              <div key={milestone.id} className="flex items-start gap-3 rounded-lg border p-4">
                {milestone.completed ? <Check className="mt-0.5 h-5 w-5 shrink-0 text-accent" /> : <Circle className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />}
                <div>
                  <p className="text-sm font-medium">{i + 1}. {milestone.title}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-4 text-lg font-semibold">Technologies</h2>
          <div className="flex flex-wrap gap-2">
            {project.technologies.map((tech) => <Badge key={tech} variant="secondary">{tech}</Badge>)}
          </div>
          <h2 className="mb-4 mt-8 text-lg font-semibold">Skills</h2>
          <div className="space-y-2">
            {project.skillsDeveloped.map((skill) => (
              <div key={skill} className="flex items-center gap-2 text-sm"><Wrench className="h-3 w-3 text-primary" />{skill}</div>
            ))}
          </div>
          <div className="mt-8">
            <Button className="w-full" disabled>Start Project</Button>
            <p className="mt-2 text-center text-xs text-muted-foreground">Coming in MVP.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
