import type { Metadata } from "next";
import Link from "next/link";
import { UserRoundX } from "lucide-react";
import { fetchPublicPortfolioServer } from "@/lib/server-portfolio";
import { PortfolioView } from "@/components/portfolio/portfolio-view";

// Rendered per request from the live API so unpublished or private work is
// never cached or leaked into the HTML.
export const dynamic = "force-dynamic";

type Outcome = Awaited<ReturnType<typeof fetchPublicPortfolioServer>>;

async function load(username: string): Promise<Outcome> {
  return fetchPublicPortfolioServer(username);
}

export async function generateMetadata({
  params,
}: { params: Promise<{ username: string }> }): Promise<Metadata> {
  const { username } = await params;
  const res = await load(username);
  if (res.state !== "ok") {
    return { title: "Portfolio unavailable", robots: { index: false, follow: false } };
  }
  const p = res.data;
  const name = p.display_name || p.username;
  const description =
    p.headline ||
    p.about?.text?.slice(0, 160) ||
    `${name}'s developer portfolio on Code Yaar.`;
  return {
    title: `${name} — Developer Portfolio`,
    description,
    // Published, public portfolio: indexable so a shared link previews well and
    // shows up in search. Private/unpublished answers never reach here.
    robots: { index: true, follow: true },
    openGraph: {
      title: `${name} — Developer Portfolio`,
      description,
      type: "profile",
      images: p.avatar ? [{ url: p.avatar }] : undefined,
    },
  };
}

export default async function PublicPortfolioPage({
  params,
}: { params: Promise<{ username: string }> }) {
  const { username } = await params;
  const res = await load(username);

  if (res.state !== "ok") {
    const unavailable = res.state === "unavailable";
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <UserRoundX className="h-6 w-6" aria-hidden="true" />
        </div>
        <h1 className="mt-4 text-xl font-bold text-foreground">
          {unavailable ? "Portfolio temporarily unavailable" : "Portfolio not found"}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {unavailable
            ? "We couldn't reach the portfolio service just now. Please try again shortly."
            : "This developer either doesn't exist, keeps their profile private, or hasn't published a portfolio yet."}
        </p>
        <Link
          href="/leaderboard"
          className="mt-6 inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
        >
          Explore the community
        </Link>
      </div>
    );
  }

  return <PortfolioView data={res.data} />;
}
