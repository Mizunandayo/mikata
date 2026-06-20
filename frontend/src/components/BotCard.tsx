import Link from "next/link";
import type { Bot } from "@/lib/types";
import PisBadge from "./PisBadge";

const LEVEL_COLOR = { 1: "var(--level-1)", 2: "var(--level-2)", 3: "var(--level-3)" } as const;



function timeAgo(iso: string | null): string {
  if (!iso) return "never tested";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  return `${Math.round(mins / 60)} h ago`;
}






export default function BotCard({ bot, index }: { bot: Bot; index: number }) {
  const failed = bot.last_test_result === "fail";
  const color = LEVEL_COLOR[bot.patient_impact_level];
  return (
    <Link
      href={`/bot/${bot.id}`}
      className={`lift animate-rise block rounded-2xl border p-5 ${failed ? "animate-failpulse" : ""}`}
      style={{
        background: "var(--surface)",
        borderColor: "var(--surface-border)",
        animationDelay: `${index * 60}ms`,
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          {bot.name}
        </h3>
        <span
          className="shrink-0 rounded-md px-2 py-1 text-sm font-bold"
          style={{
            color: failed ? "var(--level-3)" : "var(--level-1)",
            background: failed ? "#ef44441f" : "#14b8a61f",
          }}
        >
          {failed ? "FAIL" : "PASS"}
        </span>
      </div>

      <div className="mt-3">
        <PisBadge level={bot.patient_impact_level} />
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between text-sm" style={{ color: "var(--text-secondary)" }}>
          <span>Automation Debt</span>
          <span className="font-semibold" style={{ color: "var(--text-primary)" }}>
            {Math.round(bot.automation_debt_score)}
          </span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.08)" }}>
          <div
            className="ads-fill h-full rounded-full"
            style={{ width: `${bot.automation_debt_score}%`, background: color }}
          />
        </div>
      </div>

      <p className="mt-4 text-sm" style={{ color: "var(--text-secondary)" }}>
        Last test: {timeAgo(bot.last_tested_at)}
      </p>
    </Link>
  );
}
