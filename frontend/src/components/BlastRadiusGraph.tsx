"use client";

import { useMemo } from "react";
import type { BlastRadius } from "@/lib/types";




const NODE_W = 184;
const NODE_H = 78;
const COL_W = 248;
const ROW_GAP = 26;
const PAD = 28;

const LEVEL_COLOR: Record<number, string> = {
  1: "var(--level-1)",
  2: "var(--level-2)",
  3: "var(--level-3)",
};

type Placed = BlastRadius["origin"] & { x: number; y: number };







export default function BlastRadiusGraph({
  data,
  revealedDepth,
  alert,
}: {
  data: BlastRadius;
  revealedDepth: number;
  alert: boolean;
}) {
  const { placed, width, height } = useMemo(() => {
    const all = [data.origin, ...data.nodes];
    const byDepth = new Map<number, typeof all>();
    for (const n of all) {
      const arr = byDepth.get(n.depth) ?? [];
      arr.push(n);
      byDepth.set(n.depth, arr);
    }
    const maxDepth = data.summary.max_depth;
    const tallest = Math.max(...[...byDepth.values()].map((a) => a.length), 1);
    const h = PAD * 2 + tallest * NODE_H + (tallest - 1) * ROW_GAP;
    const w = PAD * 2 + maxDepth * COL_W + NODE_W;

    const map = new Map<string, Placed>();
    for (const [depth, arr] of byDepth) {
      const colH = arr.length * NODE_H + (arr.length - 1) * ROW_GAP;
      const top = (h - colH) / 2;
      arr.forEach((n, i) => {
        map.set(n.id, {
          ...n,
          x: PAD + depth * COL_W,
          y: top + i * (NODE_H + ROW_GAP),
        });
      });
    }
    return { placed: map, width: w, height: h };
  }, [data]);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      style={{ maxHeight: 420, display: "block" }}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Cascade blast radius dependency graph"
    >
      {/* Edges under the cards */}
      {data.edges.map((e) => {
        const a = placed.get(e.src);
        const b = placed.get(e.dst);
        if (!a || !b) return null;
        const sx = a.x + NODE_W;
        const sy = a.y + NODE_H / 2;
        const dx = b.x;
        const dy = b.y + NODE_H / 2;
        const mx = (sx + dx) / 2;
        const dstDepth = data.nodes.find((n) => n.id === e.dst)?.depth ?? 99;
        const on = !alert || dstDepth <= revealedDepth;
        const stroke = !alert
          ? "rgba(255,255,255,0.22)"
          : on
            ? "var(--level-2)"
            : "rgba(255,255,255,0.10)";
        return (
          <path
            key={`${e.src}-${e.dst}-${e.field}`}
            className="blast-edge"
            d={`M ${sx} ${sy} C ${mx} ${sy}, ${mx} ${dy}, ${dx} ${dy}`}
            fill="none"
            stroke={stroke}
            strokeWidth={2.5}
            strokeDasharray={e.criticality === "soft" ? "7 6" : "1"}
            pathLength={1}
            style={{ strokeDashoffset: on ? 0 : 1 }}
          >
            <title>{`${e.field} (${e.criticality})`}</title>
          </path>
        );
      })}

      {/* Node cards */}
      {[data.origin, ...data.nodes].map((n) => {
        const p = placed.get(n.id)!;
        const isOrigin = n.depth === 0;
        const revealed = !alert || isOrigin || n.depth <= revealedDepth;

        let borderColor = LEVEL_COLOR[n.level];
        let glowClass = "";
        if (alert && isOrigin) {
          borderColor = "var(--level-3)";
          glowClass = "animate-failpulse";
        } else if (alert && revealed) {
          borderColor = "var(--level-2)";
          glowClass = "animate-amberglow";
        }

        return (
          <foreignObject
            key={n.id}
            x={p.x}
            y={p.y}
            width={NODE_W}
            height={NODE_H}
          >
            <div
              className={`blast-node ${glowClass}`}
              style={{
                width: NODE_W,
                height: NODE_H,
                boxSizing: "border-box",
                borderRadius: 16,
                border: `1px solid ${borderColor}`,
                background: revealed
                  ? "rgba(255,255,255,0.06)"
                  : "rgba(255,255,255,0.02)",
                opacity: revealed ? 1 : 0.32,
                transform: revealed ? "scale(1)" : "scale(0.96)",
                padding: "10px 12px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <span
                style={{
                  color: "var(--text-primary)",
                  fontSize: 15,
                  fontWeight: 600,
                  lineHeight: 1.2,
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {n.name}
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span
                  aria-hidden
                  style={{
                    width: 9,
                    height: 9,
                    borderRadius: 999,
                    background: LEVEL_COLOR[n.level],
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    color: LEVEL_COLOR[n.level],
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  L{n.level}
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    color: "var(--text-primary)",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  {n.volume.toLocaleString()}/day
                </span>
              </span>
            </div>
          </foreignObject>
        );
      })}
    </svg>
  );
}
