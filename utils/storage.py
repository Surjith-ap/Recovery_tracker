import os
from flask import current_app
from supabase import create_client, Client
from werkzeug.utils import secure_filename

def get_supabase_client():
    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

def upload_file(file_obj, safe_name):
    """Uploads file to Supabase if configured, otherwise local disk."""
    supabase = get_supabase_client()
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
    
    # Save locally temporarily or permanently
    file_obj.save(filepath)
    file_size = os.path.getsize(filepath)

    if supabase:
        try:
            with open(filepath, 'rb') as f:
                res = supabase.storage.from_("uploads").upload(safe_name, f)
            # Remove local file if we only want it in cloud
            os.remove(filepath)
            print(f"Uploaded {safe_name} to Supabase")
        except Exception as e:
            print(f"Supabase upload failed: {e}")
            # It's saved locally as a fallback
    
    return file_size

def delete_file(safe_name):
    """Deletes file from Supabase if configured, otherwise local disk."""
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.storage.from_("uploads").remove([safe_name])
        except Exception as e:
            print(f"Supabase delete failed: {e}")
    
    # Also attempt local delete
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
    if os.path.exists(filepath):
        os.remove(filepath)

def get_file_url(safe_name):
    """Returns the public URL from Supabase, or None to use local fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.storage.from_("uploads").get_public_url(safe_name)
            return res
        except Exception as e:
            return None
    return None
