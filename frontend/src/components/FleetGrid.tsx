import type { Bot } from "@/lib/types";
import BotCard from "./BotCard";




export default function FleetGrid({ bots }: { bots: Bot[] }) {
  return (
    <div className="grid grid-cols-1 gap-5 px-8 py-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {bots.map((bot, i) => <BotCard key={bot.id} bot={bot} index={i} />)}
    </div>
  );
}
