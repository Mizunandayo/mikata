import Link from "next/link";
import RegisterForm from "@/components/RegisterForm";




export default function RegisterPage() {
  return (
    <main className="mx-auto max-w-2xl px-8 py-12">
      <Link href="/" className="text-base" style={{ color: "var(--text-secondary)" }}>
        ← Back to fleet
      </Link>
      <h1 className="mt-4 mb-8 text-3xl font-bold" style={{ color: "var(--text-primary)" }}>
        Register an automation
      </h1>
      <RegisterForm />
    </main>
  );
}
