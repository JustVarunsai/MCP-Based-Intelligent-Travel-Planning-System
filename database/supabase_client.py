from supabase import create_client, Client
from config import config


def get_supabase() -> Client:
    """Return a Supabase client using keys from config / session state."""
    return create_client(config.supabase_url, config.supabase_key)
