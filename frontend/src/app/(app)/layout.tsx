import { Suspense } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col bg-[#f5f7fa]">
      <Suspense fallback={null}>
        <AppSidebar />
      </Suspense>
      {/* Main content area — offset for sidebar on desktop, offset for mobile header */}
      <div className="flex min-h-0 flex-1 flex-col pt-14 md:pl-[272px] md:pt-0">
        <main className="min-h-0 flex-1">
          <Suspense fallback={null}>{children}</Suspense>
        </main>
      </div>
    </div>
  );
}
