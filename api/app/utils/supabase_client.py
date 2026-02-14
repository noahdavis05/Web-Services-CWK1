from ..config import settings
from supabase import create_client, Client


supabase: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_ANON_KEY
)