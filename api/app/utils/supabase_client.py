from ..config import settings
from supabase import create_client, Client


if settings.AUTHENTICATION_ON:
    supabase: Client = create_client(
        settings.SUPABASE_URL, 
        settings.SUPABASE_PUBLIC_KEY
    )
else:
    supabase = None