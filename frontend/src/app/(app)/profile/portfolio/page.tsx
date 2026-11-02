"use client";

// Standalone route kept alive for bookmarks and inbound links; it renders the
// same shared portfolio body as the My Profile > Portfolio tab.
import { PortfolioDashboard } from "@/components/portfolio/portfolio-dashboard";

export default function PortfolioDashboardPage() {
  return <PortfolioDashboard />;
}
