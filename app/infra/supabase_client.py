from supabase import create_client, Client
from app.config.settings import settings

class SupabaseClientWrapper:
    _instance: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("Supabase URL and Service Role Key must be set")
            cls._instance = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return cls._instance

def list_files(prefix: str | None = None) -> list[str]:
    client = SupabaseClientWrapper.get_client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    
    # 'list' method usually takes a path/prefix. If prefix is None, we might want root.
    # Supabase-py storage list signature: storage.from_(bucket).list(path, "options")
    # path defaults to root if logic suggests so.
    
    path = prefix if prefix else ""
    
    # storage.from_ returns a StorageFileApi
    # list returns a list of dictionaries (metadata)
    response = client.storage.from_(bucket).list(path)
    
    if not isinstance(response, list):
         # Handle potential unexpected response types if library changes, though usually it's list of dicts.
         return []

    # Filter out folders if necessary or just return names. 
    # Usually we want full paths relative to bucket or just names. 
    # Request says "list files", so returning names. 
    # If prefix was used, result names are relative to prefix.
    return [item['name'] for item in response if 'name' in item]

def download_file(path: str) -> bytes:
    client = SupabaseClientWrapper.get_client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    
    response = client.storage.from_(bucket).download(path)
    return response

# Initialize on module load if preferred, or keep lazy.
# The request asked for "singleton client". The wrapper above handles it lazily.
