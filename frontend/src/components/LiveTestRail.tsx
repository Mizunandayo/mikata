"use client";

import { useEffect, useState } from "react";
import { openEventStream, type MikataEvent } from "@/lib/ws";



const STATUS_COLOR: Record<string, string> = {
  passed: "var(--level-1)", pass: "var(--level-1)",
  failed: "var(--level-3)", fail: "var(--level-3)", error: "var(--level-3)",
  running: "var(--level-2)", injecting: "var(--level-2)", timeout: "var(--level-2)",
  queued: "var(--text-secondary)",
};




export default function LiveTestRail() {
  const [events, setEvents] = useState<MikataEvent[]>([]);
  const [live, setLive] = useState(false);

  useEffect(() => {
    let close = () => {};
    openEventStream((e) => {
      if (e.type === "connected") { setLive(true); return; }
      if (e.type === "blast_radius") return;   // handled by BlastRadiusPanel, not the rail
      setEvents((prev) => [e, ...prev].slice(0, 8));
    }).then((c) => (close = c)).catch(() => setLive(false));
    return () => close();
  }, []);




  return (
    <section className="px-8 pb-6">
      <div className="flex items-center gap-3 pb-3">
        <span className="inline-block h-3 w-3 rounded-full"
          style={{ background: live ? "var(--level-1)" : "var(--text-tertiary)",
                   boxShadow: live ? "0 0 12px 2px rgba(20,184,166,0.6)" : "none" }} />
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          {live ? "Live test stream" : "Connecting to test stream"}
        </h2>
      </div>
      <div className="flex flex-col gap-2">
        {events.map((e, i) => (
          <div key={`${e.run_id}-${i}`}
            className="animate-rise flex items-center justify-between rounded-xl border px-4 py-3"
            style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}>
            <span className="font-medium" style={{ color: "var(--text-primary)" }}>
              {e.bot_name ?? "Synthetic patient test"}{e.detail ? ` — ${e.detail}` : ""}
            </span>
            <span className="rounded-md px-2 py-1 text-sm font-bold uppercase"
              style={{ color: STATUS_COLOR[e.status ?? ""] ?? "var(--text-primary)",
                       background: "rgba(255,255,255,0.06)" }}>
              {e.status ?? e.type}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
