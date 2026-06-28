"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { BlastRadius } from "@/lib/types";
import { openEventStream } from "@/lib/ws";
import BlastRadiusGraph from "./BlastRadiusGraph";





const STEP_MS = 700; 




function useCountUp(target: number, ms = 600): number {
  const [value, setValue] = useState(target);
  const fromRef = useRef(target);
  useEffect(() => {
    const from = fromRef.current;
    const start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / ms);
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(Math.round(from + (target - from) * eased));
      if (t < 1) raf = requestAnimationFrame(tick);
      else fromRef.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);
  return value;
}




export default function BlastRadiusPanel({
  initial,
  demoBotId,
  onSimulate,
}: {
  initial: BlastRadius | null;
  demoBotId: string;
  onSimulate: (botId: string) => Promise<void>;
}) {
  const [data, setData] = useState<BlastRadius | null>(initial);
  const [revealedDepth, setRevealedDepth] = useState(initial?.summary.max_depth ?? 0);
  const [alert, setAlert] = useState(false);
  const [pending, setPending] = useState(false);
  const timers = useRef<number[]>([]);

  const play = useCallback((blast: BlastRadius) => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setData(blast);
    setAlert(true);
    setRevealedDepth(0);
    for (let d = 1; d <= blast.summary.max_depth; d++) {
      timers.current.push(
        window.setTimeout(() => setRevealedDepth(d), d * STEP_MS),
      );
    }
  }, []);

  useEffect(() => {
    let close = () => {};
    openEventStream((e) => {
      if (e.type === "blast_radius" && e.blast) play(e.blast);
    })
      .then((c) => (close = c))
      .catch(() => {});
    return () => {
      close();
      timers.current.forEach(clearTimeout);
    };
  }, [play]);

  const trigger = async () => {
    setPending(true);
    try {
      await onSimulate(demoBotId);
    } finally {
      setPending(false);
    }
  };

  // Patients at risk so far: downstream nodes revealed up to revealedDepth.
  const revealedVolume = data
    ? alert
      ? data.nodes
          .filter((n) => n.depth <= revealedDepth)
          .reduce((s, n) => s + n.volume, 0)
      : data.summary.patient_volume_24h
    : 0;
  const counted = useCountUp(revealedVolume);

  if (!data) return null;




  return (
    <section
      className="mx-8 mb-6 rounded-2xl border p-6"
      style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
            Cascade blast radius
          </h2>
          <p className="mt-1 text-base" style={{ color: "var(--text-primary)" }}>
            {alert ? (
              <span style={{ color: "var(--level-3)", fontWeight: 600 }}>
                {data.origin.name} failed — illuminating downstream impact
              </span>
            ) : (
              <span>Live dependency map · {data.origin.name}</span>
            )}
          </p>
        </div>
        <button
          onClick={trigger}
          disabled={pending}
          className="lift rounded-xl px-5 py-3 text-base font-semibold transition"
          style={{
            background: pending ? "var(--surface)" : "var(--level-3)",
            color: pending ? "var(--text-primary)" : "#2a0606",
            opacity: pending ? 0.7 : 1,
          }}
        >
          {pending ? "Simulating cascade…" : "Simulate failure cascade"}
        </button>
      </div>

      {/* Stat row */}
      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Automations affected" value={data.summary.affected_bots} accent="var(--level-2)" />
        <Stat label="Patients at risk · next 24h" value={counted} accent="var(--level-3)" />
        <Stat label="Aggregate Patient Impact" value={data.summary.aggregate_pis} accent="var(--level-1)" />
      </div>

      <div className="mt-6 overflow-x-auto">
        <BlastRadiusGraph data={data} revealedDepth={revealedDepth} alert={alert} />
      </div>

      <Legend />
    </section>
  );
}




function Stat({ label, value, accent }: { label: string; value: number; accent: string }) {
  return (
    <div
      className="rounded-xl border px-5 py-4"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "var(--surface-border)" }}
    >
      <p className="text-3xl font-bold tabular-nums" style={{ color: accent }}>
        {value.toLocaleString()}
      </p>
      <p className="mt-1 text-base" style={{ color: "var(--text-primary)" }}>
        {label}
      </p>
    </div>
  );
}




function Legend() {
  return (
    <div className="mt-5 flex flex-wrap items-center gap-6 text-base" style={{ color: "var(--text-primary)" }}>
      <Swatch color="var(--level-3)" text="Failed origin" />
      <Swatch color="var(--level-2)" text="Downstream at risk" />
      <span className="inline-flex items-center gap-2">
        <svg width="34" height="10" aria-hidden>
          <line x1="0" y1="5" x2="34" y2="5" stroke="var(--text-primary)" strokeWidth="2.5" />
        </svg>
        Hard dependency
      </span>
      <span className="inline-flex items-center gap-2">
        <svg width="34" height="10" aria-hidden>
          <line x1="0" y1="5" x2="34" y2="5" stroke="var(--text-primary)" strokeWidth="2.5" strokeDasharray="7 6" />
        </svg>
        Soft dependency
      </span>
    </div>
  );
}

function Swatch({ color, text }: { color: string; text: string }) {
  return (
    <span className="inline-flex items-center gap-2">
      <span style={{ width: 14, height: 14, borderRadius: 4, background: color, display: "inline-block" }} />
      {text}
    </span>
  );
}
