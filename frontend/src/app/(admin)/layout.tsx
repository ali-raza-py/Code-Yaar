"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Suspense, useState } from "react";
import { AdminSidebar } from "@/components/admin/admin-sidebar";
import { AdminTopNav } from "@/components/admin/admin-top-nav";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/sign-in");
      return;
    }
    if (user.role !== "administrator") {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh bg-background">
      <Suspense fallback={null}>
        <AdminSidebar collapsed={sidebarCollapsed} onToggle={setSidebarCollapsed} />
      </Suspense>
      <div
        className={cn(
          "flex min-h-0 flex-1 flex-col",
          sidebarCollapsed ? "lg:pl-0" : "lg:pl-[280px]"
        )}
      >
        <AdminTopNav onMenuClick={() => setSidebarCollapsed(false)} />
        <main className="min-h-0 flex-1 p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}