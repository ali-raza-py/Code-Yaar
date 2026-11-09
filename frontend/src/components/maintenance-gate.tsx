"use client";

import { useEffect, useState } from "react";
import { request } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

interface PlatformStatus {
  maintenance_mode: boolean;
  maintenance_message: string;
  estimated_return_time: string;
}

export function MaintenanceGate({ children }: { children: React.ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [status, setStatus] = useState<PlatformStatus | null>(null);

  useEffect(() => {
    let active = true;
    const loadStatus = () => {
      request<PlatformStatus>("/platform/status/", {
        withAuth: false,
        retryOnUnauthorized: false,
      })
        .then((data) => {
          if (active) setStatus(data);
        })
        .catch(() => {
          // Do not lock users out when the status endpoint itself is unavailable.
        });
    };
    loadStatus();
    const interval = window.setInterval(loadStatus, 15000);
    const onStatusChange = (event: Event) => {
      const next = (event as CustomEvent<PlatformStatus>).detail;
      if (next) setStatus(next);
    };
    window.addEventListener("maintenance-status-changed", onStatusChange);
    return () => {
      active = false;
      window.clearInterval(interval);
      window.removeEventListener("maintenance-status-changed", onStatusChange);
    };
  }, []);

  const isSuperAdmin = user?.is_super_admin === true;
  if (!authLoading && status?.maintenance_mode && !isSuperAdmin) {
    return (
      <main className="flex min-h-dvh items-center justify-center bg-background px-6 py-16">
        <div className="w-full max-w-lg text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-3xl">
            🔧
          </div>
          <h1 className="text-3xl font-bold text-foreground">We&apos;ll be back soon</h1>
          <p className="mt-4 text-muted-foreground">
            {status.maintenance_message ||
              "We are making improvements and will be back shortly."}
          </p>
          {status.estimated_return_time && (
            <p className="mt-3 text-sm text-muted-foreground">
              Estimated return: {status.estimated_return_time}
            </p>
          )}
          <p className="mt-6 text-sm text-muted-foreground">
            Please check back in a little while.
          </p>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
