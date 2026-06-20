import TopBar from "@/components/TopBar";
import FleetGrid from "@/components/FleetGrid";
import LiveTestRail from "@/components/LiveTestRail";
import RunTestButton from "@/components/RunTestButton";
import { getFleet } from "@/lib/api";
import { runTestAction } from "./actions";

export default async function Home() {
  const fleet = await getFleet();
  // Prior Authorization Bot is the demo target; fall back to first bot.
  const demoBot =
    fleet.bots.find((b) => b.name.toLowerCase().includes("prior auth")) ?? fleet.bots[0];

  return (
    <main>
      <TopBar hospital={fleet.hospital} count={fleet.bot_count} />

      <div className="flex items-start justify-between gap-4 px-8 pt-2">
        <LiveTestRail />
        {demoBot && (
          <div className="shrink-0 pt-1">
            <RunTestButton botId={demoBot.id} action={runTestAction} />
          </div>
        )}
      </div>

      <FleetGrid bots={fleet.bots} />
    </main>
  );
}
