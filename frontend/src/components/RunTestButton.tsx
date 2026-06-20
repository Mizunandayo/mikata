"use client";

import { useTransition } from "react";



export default function RunTestButton({ botId, action }: {
  botId: string; action: (botId: string) => Promise<void>;
}) {
  const [pending, startTransition] = useTransition();
  return (
    <button
      onClick={() => startTransition(() => action(botId))}
      disabled={pending}
      className="lift rounded-xl px-5 py-3 text-base font-semibold transition"
      style={{ background: pending ? "var(--surface)" : "var(--level-1)",
               color: pending ? "var(--text-secondary)" : "#04211d",
               opacity: pending ? 0.7 : 1 }}>
      {pending ? "Running synthetic patient test…" : "Run synthetic patient test"}
    </button>
  );
}