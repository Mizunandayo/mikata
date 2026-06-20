import json
import subprocess
import tempfile
from pathlib import Path
from app.config import settings





def generate_cohort(count: int = 10, seed: int = 20260619) -> list[dict]:
    """Run Synthea, return parsed patient summaries. Seed-time use only."""
    if not settings.synthea_jar_path:
        raise RuntimeError("SYNTHEA_JAR_PATH not configured")

    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            "java", "-jar", settings.synthea_jar_path,
            "-p", str(count),
            "-s", str(seed),               
            "--exporter.fhir.export", "true",
            "--exporter.hospital.fhir.export", "false",
            "--exporter.practitioner.fhir.export", "false",
            "--exporter.baseDirectory", tmp,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)

        fhir_dir = Path(tmp) / "fhir"
        patients: list[dict] = []
        for bundle_path in sorted(fhir_dir.glob("*.json")):
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            summary = _summarize_bundle(bundle)
            if summary:
                patients.append({"fhir_bundle": bundle, "summary": summary,
                                 "synthea_id": summary["synthea_id"]})
        return patients[:count]
    






def _summarize_bundle(bundle: dict) -> dict | None:
    """Flatten the FHIR R4 Patient + first Condition/Coverage into a demo summary."""
    entries = bundle.get("entry", [])
    patient = next((e["resource"] for e in entries
                    if e.get("resource", {}).get("resourceType") == "Patient"), None)
    if not patient:
        return None

    name = patient.get("name", [{}])[0]
    given = " ".join(name.get("given", []))
    family = name.get("family", "")

    conditions = [
        e["resource"]["code"]["text"]
        for e in entries
        if e.get("resource", {}).get("resourceType") == "Condition"
        and e["resource"].get("code", {}).get("text")
    ]
    coverage = next((e["resource"] for e in entries
                     if e.get("resource", {}).get("resourceType") == "Coverage"), {})

    return {
        "synthea_id": patient.get("id", ""),
        "name": f"{given} {family}".strip(),
        "gender": patient.get("gender"),
        "birth_date": patient.get("birthDate"),
        "marital_status": patient.get("maritalStatus", {}).get("text"),
        "conditions": conditions[:5],
        "insurance": coverage.get("type", {}).get("text"),
    }