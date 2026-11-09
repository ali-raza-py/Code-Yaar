"use client";

import { useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailAutomationAdmin } from "@/lib/admin-api";

export default function EmailAutomationsPage() {
  const [rules, setRules] = useState<EmailAutomationAdmin[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    adminApi.listEmailAutomations().then((r) => {
      setRules(r.results);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(load, []);

  const toggle = async (id: number) => {
    await adminApi.toggleEmailAutomation(id);
    load();
  };

  if (loading) return <div className="p-6">Loading automations…</div>;

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Automation Rules</h1>
      <table className="w-full text-sm border">
        <thead>
          <tr className="border-b">
            <th className="text-left p-2">Name</th>
            <th className="text-left p-2">Trigger</th>
            <th className="text-left p-2">Theme</th>
            <th className="text-left p-2">Enabled</th>
            <th className="text-left p-2">Runs</th>
          </tr>
        </thead>
        <tbody>
          {rules.map((r) => (
            <tr key={r.id} className="border-b">
              <td className="p-2">{r.name}</td>
              <td className="p-2">{r.trigger}</td>
              <td className="p-2">{r.theme}</td>
              <td className="p-2">
                <button onClick={() => toggle(r.id)} className="underline">
                  {r.enabled ? "Enabled" : "Disabled"}
                </button>
              </td>
              <td className="p-2">{r.success_count}/{r.failure_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}