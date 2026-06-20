export type MikataEvent = {
  type: string; run_id?: string; bot_id?: string; bot_name?: string;
  status?: string; detail?: string; last_test_result?: string;
};



const WS_BASE = process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000";




export async function openEventStream(
  onEvent: (e: MikataEvent) => void,
): Promise<() => void> {
  const res = await fetch("/api/ws-ticket", { method: "POST" });
  if (!res.ok) throw new Error("ticket fetch failed");
  const { ticket } = await res.json();
  const socket = new WebSocket(`${WS_BASE}/ws/events?ticket=${encodeURIComponent(ticket)}`);
  socket.onmessage = (ev) => { try { onEvent(JSON.parse(ev.data)); } catch {} };
  return () => socket.close();
}