// src/components/RegisterForm.tsx
"use client";

import { useActionState } from "react";
import { registerAction } from "@/app/register/action";




export default function RegisterForm() {
  const [state, action, pending] = useActionState(registerAction, null);
  return (
    <form action={action} className="flex flex-col gap-5">
      <label className="flex flex-col gap-2">
        <span className="text-base font-medium" style={{ color: "var(--text-secondary)" }}>
          Automation name
        </span>
        <input
          name="name" required maxLength={120}
          className="rounded-xl border bg-transparent px-4 py-3 text-base outline-none"
          style={{ borderColor: "var(--surface-border)", color: "var(--text-primary)" }}
        />
      </label>
      <label className="flex flex-col gap-2">
        <span className="text-base font-medium" style={{ color: "var(--text-secondary)" }}>
          What does it do? (Gemini classifies the Patient Impact Score from this)
        </span>
        <textarea
          name="description" required minLength={10} maxLength={4000} rows={5}
          className="rounded-xl border bg-transparent px-4 py-3 text-base outline-none"
          style={{ borderColor: "var(--surface-border)", color: "var(--text-primary)" }}
        />
      </label>
      {state?.error && (
        <p className="text-base" style={{ color: "var(--level-3)" }}>{state.error}</p>
      )}
      <button
        type="submit" disabled={pending}
        className="rounded-xl px-5 py-3 text-base font-semibold disabled:opacity-60"
        style={{ color: "#050505", background: "var(--text-primary)" }}
      >
        {pending ? "Classifying with Gemini…" : "Register and classify"}
      </button>
    </form>
  );
}
