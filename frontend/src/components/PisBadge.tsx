const MAP = {
  1: { label: "LEVEL 1 · ADMINISTRATIVE", color: "var(--level-1)" },
  2: { label: "LEVEL 2 · OPERATIONAL", color: "var(--level-2)" },
  3: { label: "LEVEL 3 · CLINICAL", color: "var(--level-3)" },
} as const;





export default function PisBadge({ level }: { level: 1 | 2 | 3 }) {
  const { label, color } = MAP[level];
  return (
    <span
      className="inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold"
      style={{ color, backgroundColor: `${color}1f`, border: `1px solid ${color}55` }}
    >
      {label}
    </span>
  );
}