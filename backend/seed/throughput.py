"""Idempotent per-bot 24h volume seed."""


import asyncio
from app.db  import init_pool, close_pool, get_pool


# estimated automations processed per bot per 24h at st. raphael.
DAILY_VOLUME: dict[str, int] = {
    "Eligibility Verification Bot": 2400,
    "Patient Registration Bot": 2400,
    "Prior Authorization Bot": 2400,
    "Claims Submission Bot": 1800,
    "Remittance Processing Bot": 1500,
    "Discharge Summary Bot": 1200,
    "Medication Order Processing Bot": 3000,
    "Lab Result Routing Bot": 800,
    "Critical Value Notification Bot": 200,
    "Billing Reconciliation Bot": 900,
    "Scheduling Reminder Bot": 5000,
    "Monthly Report Generation Bot": 30,
}




async def seed() -> None:
    await init_pool()
    pool = get_pool()
    updated = 0
    for name, volume in DAILY_VOLUME.items():
        result = await pool.execute(
            "UPDATE bots SET daily_patient_volume = $2 WHERE name = $1",
            name, volume,
        )
        # asyncpg returns e.g. "UPDATE 1"
        updated += int(result.split()[-1])
    await close_pool()
    print(f"Set daily_patient_volume on {updated} bots.")


if __name__ == "__main__":
    asyncio.run(seed())