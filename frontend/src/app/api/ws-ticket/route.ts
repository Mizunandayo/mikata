import { NextResponse } from "next/server";
import { getWsTicket } from "@/lib/api";






export async function POST() {
  try {
    const { ticket, expires_in } = await getWsTicket();
    return NextResponse.json({ ticket, expires_in });
  } catch {
    return NextResponse.json({ error: "ticket_unavailable" }, { status: 502 });
  }
}
