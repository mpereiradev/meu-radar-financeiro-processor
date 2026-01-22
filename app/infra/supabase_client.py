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
    
    path = prefix if prefix else ""
    
    response = client.storage.from_(bucket).list(path)
    
    if not isinstance(response, list):
        return []

    return [item['name'] for item in response if 'name' in item]

def download_file(path: str) -> bytes:
    client = SupabaseClientWrapper.get_client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    
    response = client.storage.from_(bucket).download(path)
    return response

def upload_file(bucket: str, path: str, data: bytes | str, content_type: str = "application/json") -> None:
    client = SupabaseClientWrapper.get_client()
    client.storage.from_(bucket).upload(path, data, {"content-type": content_type})

def delete_file(bucket: str, path: str) -> None:
    client = SupabaseClientWrapper.get_client()
    client.storage.from_(bucket).remove([path])

def move_file(source_bucket: str, source_path: str, dest_bucket: str, dest_path: str) -> None:
    """
    Moves a file from one bucket to another by downloading and re-uploading,
    then deleting the original.
    """
    client = SupabaseClientWrapper.get_client()
    
    # 1. Download
    file_bytes = client.storage.from_(source_bucket).download(source_path)
    
    # 2. Upload to destination
    # Determine content type (heuristic or default)
    content_type = "application/octet-stream"
    if source_path.endswith(".json"):
        content_type = "application/json"
    elif source_path.endswith(".pdf"):
        content_type = "application/pdf"
        
    client.storage.from_(dest_bucket).upload(dest_path, file_bytes, {"content-type": content_type})
    
    # 3. Delete original
    client.storage.from_(source_bucket).remove([source_path])
