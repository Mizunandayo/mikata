from pathlib import Path

from pydantic_settings import BaseSettings

# backend/.env — resolved absolutely so it loads regardless of the current
# working directory (uvicorn from repo root, scripts from backend/, etc.).
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    demo_api_key: str = "dev-only-placeholder-key"

    database_url: str = ""
    redis_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    langsmith_api_key: str = ""       
    langsmith_project: str = "mikata" 

    uipath_org_name: str = ""
    uipath_tenant_name: str = ""
    uipath_client_id: str = ""
    uipath_client_secret: str = ""
    uipath_base_url: str = "https://cloud.uipath.com"
    uipath_token_scope: str = "OR.Default"
    uipath_folder_id: str = ""
    uipath_queue_name: str = "SyntheticPatients"
    uipath_demo_test_set_id: str = ""
    uipath_poll_timeout_s: int = 180
    uipath_poll_interval_s: float = 5.0

    ws_ticket_secret: str = ""
    ws_ticket_ttl_s: int = 60


    # Comma-separated allowlist for CORS. Locked down in prod.
    cors_allow_origins: str = "http://localhost:3000"

    # Absolute path to synthea-with-dependencies.jar (seed-time only).
    synthea_jar_path: str = ""

    class Config:
        env_file = str(ENV_FILE)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


settings = Settings()
