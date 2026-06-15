import asyncio
import json
from app.config import settings
from app.db import init_pool, close_pool, get_pool
from app.services import synthea






COHORT_SIZE = 10
SEED = 20260619





def _profile_for(summary: dict) -> str:
    """Coarse clinical bucket used by Shift-Aware Scheduling (F5) and Cohort Bias (F9)."""
    birth = summary.get("birth_date") or ""
    year = int(birth[:4]) if birth[:4].isdigit() else 0
    age = 2026 - year if year else None
    conditions = " ".join(summary.get("conditions") or []).lower()

    if any(k in conditions for k in ("cancer", "neoplasm", "carcinoma", "tumor")):
        return "oncology"
    if age is not None and age < 18:
        return "pediatric"
    if age is not None and age >= 65:
        return "geriatric"
    if any(k in conditions for k in ("diabet", "hypertension", "asthma", "copd")):
        return "chronic"
    return "general"







async def seed() -> None:
    if not settings.synthea_jar_path:
        raise SystemExit("SYNTHEA_JAR_PATH not set in backend/.env")


    print(f"Generating {COHORT_SIZE} synthetic patients (seed={SEED})...")
    cohort = synthea.generate_cohort(count=COHORT_SIZE, seed=SEED)


    await init_pool()
    pool = get_pool()


    # Idempotent reset of the demo cohort.
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE synthetic_patients")
    

    for p in cohort:
        summary = p["summary"]
        profile = _profile_for(summary)
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO synthetic_patients "
                "(synthea_id, profile, fhir_bundle, summary) "
                "VALUES ($1, $2, $3, $4)",
                p["synthea_id"],
                profile,
                json.dumps(p["fhir_bundle"]),
                json.dumps(summary),
                timeout=60, 
            )
        print(f"  {profile:<10} {summary.get('name','(no name)')}")

    await close_pool()
    print(f"Seeded {len(cohort)} synthetic patients.")


if __name__ == "__main__":
    asyncio.run(seed())
