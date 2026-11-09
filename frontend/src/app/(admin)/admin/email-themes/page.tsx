"use client";

import { useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailThemeAdmin } from "@/lib/admin-api";

export default function EmailThemesPage() {
  const [themes, setThemes] = useState<EmailThemeAdmin[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.listEmailThemes().then((r) => {
      setThemes(r.results);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading themes…</div>;

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Theme Gallery</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {themes.map((t) => (
          <div key={t.id} className="border rounded-lg p-4" style={{ backgroundColor: t.background_color }}>
            <div className="font-semibold" style={{ color: t.primary_color }}>{t.name}</div>
            <p className="text-sm mt-1">{t.description}</p>
            <p className="text-xs mt-2 opacity-70">Best for: {t.best_for}</p>
            <div className="flex gap-2 mt-3">
              <span className="w-5 h-5 rounded" style={{ backgroundColor: t.primary_color }} />
              <span className="w-5 h-5 rounded" style={{ backgroundColor: t.accent_color }} />
              <span className="w-5 h-5 rounded" style={{ backgroundColor: t.highlight_color }} />
            </div>
            {t.is_default && <span className="text-xs mt-2 inline-block">Default</span>}
          </div>
        ))}
      </div>
    </div>
  );
}