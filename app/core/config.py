import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://xyzcompany.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your_anon_key")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/tasks"
    )
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
