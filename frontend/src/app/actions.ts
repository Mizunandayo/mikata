"use server";
import { runTest, simulateBlast } from "@/lib/api";




export async function runTestAction(botId: string) {
  await runTest(botId);   
}

export async function simulateBlastAction(botId: string) {
  await simulateBlast(botId);
}