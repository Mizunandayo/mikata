import TopBar from "@/components/TopBar";
import FleetGrid from "@/components/FleetGrid";
import LiveTestRail from "@/components/LiveTestRail";
import RunTestButton from "@/components/RunTestButton";
import BlastRadiusPanel from "@/components/BlastRadiusPanel";
import { getFleet, getBlastRadius } from "@/lib/api";
import { runTestAction, simulateBlastAction } from "./actions";



export default async function Home() {
  const fleet = await getFleet();
  const demoBot =
    fleet.bots.find((b) => b.name.toLowerCase().includes("prior auth")) ?? fleet.bots[0];


  // Initial cascade map, fetched server-side (key never reaches the browser).
  const blast = demoBot ? await getBlastRadius(demoBot.id).catch(() => null) : null;

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

      {demoBot && (
        <BlastRadiusPanel
          initial={blast}
          demoBotId={demoBot.id}
          onSimulate={simulateBlastAction}
        />
      )}

      <FleetGrid bots={fleet.bots} />
    </main>
  );
}
