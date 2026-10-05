import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("uvicorn")

supabase: Client = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Server running and connected to Supabase")
except Exception as e:
    logger.warning(f"Could not connect to Supabase: {e}")


def get_supabase_client() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase
