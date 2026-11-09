import type { Metadata } from "next";
import Link from "next/link";
import { FileQuestion } from "lucide-react";
import { fetchPublicProjectServer } from "@/lib/server-portfolio";
import { ProjectDetails } from "@/components/portfolio/project-details";

export const dynamic = "force-dynamic";

type Outcome = Awaited<ReturnType<typeof fetchPublicProjectServer>>;

async function load(username: string, slug: string): Promise<Outcome> {
  return fetchPublicProjectServer(username, slug);
}

export async function generateMetadata({
  params,
}: { params: Promise<{ username: string; slug: string }> }): Promise<Metadata> {
  const { username, slug } = await params;
  const res = await load(username, slug);
  if (res.state !== "ok") {
    return { title: "Project unavailable", robots: { index: false, follow: false } };
  }
  const project = res.data;
  const description =
    project.short_description ||
    project.overview?.slice(0, 160) ||
    `${project.title} — a project by ${username} on Code Yaar.`;
  return {
    title: `${project.title} — ${username}`,
    description,
    robots: { index: true, follow: true },
    openGraph: {
      title: project.title,
      description,
      type: "article",
      images: project.cover_image_url ? [{ url: project.cover_image_url }] : undefined,
    },
  };
}

export default async function PublicProjectPage({
  params,
}: { params: Promise<{ username: string; slug: string }> }) {
  const { username, slug } = await params;
  const res = await load(username, slug);

  if (res.state !== "ok") {
    const unavailable = res.state === "unavailable";
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <FileQuestion className="h-6 w-6" aria-hidden="true" />
        </div>
        <h1 className="mt-4 text-xl font-bold text-foreground">
          {unavailable ? "Project temporarily unavailable" : "Project not found"}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {unavailable
            ? "We couldn't reach the portfolio service just now. Please try again shortly."
            : "This project is private, unpublished, or no longer exists."}
        </p>
        <Link
          href={`/profile/${username}/portfolio`}
          className="mt-6 inline-flex min-h-10 items-center rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
        >
          View portfolio
        </Link>
      </div>
    );
  }

  return <ProjectDetails project={res.data} username={username} />;
}
