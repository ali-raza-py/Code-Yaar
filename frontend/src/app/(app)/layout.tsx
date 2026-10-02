import { Suspense } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f5f7fa]">
      <Suspense fallback={null}>
        <AppSidebar />
      </Suspense>
      {/* Main content area — offset for sidebar on desktop, offset for mobile header */}
      <div className="lg:pl-60 pt-14 lg:pt-0">
        <main className="min-h-[calc(100vh-3.5rem)] lg:min-h-screen">
          <Suspense fallback={null}>{children}</Suspense>
        </main>
      </div>
    </div>
  );
}
