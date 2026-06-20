import TopBar from "@/components/TopBar";
import FleetGrid from "@/components/FleetGrid";
import { getFleet } from "@/lib/api";

export default async function Home() {
  const fleet = await getFleet();
  return (
    <main>
      <TopBar hospital={fleet.hospital} count={fleet.bot_count} />
      <FleetGrid bots={fleet.bots} />
    </main>
  );
}
