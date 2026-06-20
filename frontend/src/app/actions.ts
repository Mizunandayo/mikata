"use server";
import { runTest } from "@/lib/api";




export async function runTestAction(botId: string) {
  await runTest(botId);   
}
