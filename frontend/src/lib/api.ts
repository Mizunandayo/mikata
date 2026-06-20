import "server-only";
import type { Fleet } from "./types";



const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const KEY = process.env.DEMO_API_KEY ?? "";




async function backend<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "x-api-key": KEY, "content-type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store", // fleet state is live; never serve stale
  });
  if (!res.ok) throw new Error(`backend ${path} -> ${res.status}`);
  return res.json() as Promise<T>;
}



export const getFleet = () => backend<Fleet>("/api/v1/fleet");



export const registerBot = (name: string, description: string) =>
  backend("/api/v1/fleet/register", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });