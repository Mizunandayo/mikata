"use server";


import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { registerBot } from "@/lib/api";





export async function registerAction(_prev: unknown, formData: FormData) {
  const name = String(formData.get("name") ?? "").trim();
  const description = String(formData.get("description") ?? "").trim();
  if (name.length < 1 || description.length < 10) {
    return { error: "Name is required and description must be at least 10 characters." };
  }
  try {
    await registerBot(name, description);
  } catch {
    return { error: "Registration failed. Check the backend is reachable." };
  }
  revalidatePath("/");
  redirect("/");
}

