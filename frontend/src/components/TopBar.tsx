import Link from "next/link";





export default function TopBar({ hospital, count }: { hospital: string; count: number }) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b px-8 py-6"
            style={{ borderColor: "var(--surface-border)" }}>
      <div>
        <p className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
          MIKATA <span style={{ color: "var(--text-secondary)" }}>味方</span>
        </p>
        <p className="mt-1 text-base" style={{ color: "var(--text-secondary)" }}>
          Clinical Automation Safety System · {hospital} · {count} automations monitored
        </p>
      </div>
      <Link href="/register"
            className="rounded-xl px-5 py-3 text-base font-semibold"
            style={{ color: "#050505", background: "var(--text-primary)" }}>
        Register automation
      </Link>
    </header>
  );
}
