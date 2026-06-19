def to_queue_payload(patient_summary: dict, run_id: str) -> dict:
    conditions = patient_summary.get("conditions") or []
    return {
        "run_id": run_id,
        "synthetic": True,
        "patient_name": str(patient_summary.get("name", ""))[:120],
        "diagnosis_code": str(conditions[0]) if conditions else "",
        "procedure_code": "99213",
        "insurance": str(patient_summary.get("insurance", ""))[:120],
        "gender": str(patient_summary.get("gender", ""))[:16],
        "birth_date": str(patient_summary.get("birth_date", ""))[:10],
    }


