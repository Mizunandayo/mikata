from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    demo_api_key: str = "dev-only-placeholder-key"

    database_url: str = ""
    redis_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    gemini_api_key: str = ""

    uipath_org_name: str = ""
    uipath_tenant_name: str = ""
    uipath_client_id: str = ""
    uipath_client_secret: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
