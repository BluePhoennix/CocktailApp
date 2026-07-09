import secrets

from supabase_client import get_client


def create_profile(user_id):
    client = get_client()
    share_code = secrets.token_urlsafe(8)
    client.table("profiles").insert({"user_id": user_id, "share_code": share_code}).execute()
    return share_code


def get_share_code(user_id):
    client = get_client()
    result = client.table("profiles").select("share_code").eq("user_id", user_id).execute()
    return result.data[0]["share_code"] if result.data else None


def get_profile(user_id):
    client = get_client()
    result = client.table("profiles").select("share_code, bar_name").eq("user_id", user_id).execute()
    return result.data[0] if result.data else None


def update_bar_name(user_id, bar_name):
    client = get_client()
    client.table("profiles").update({"bar_name": bar_name}).eq("user_id", user_id).execute()


def get_user_id_by_share_code(share_code):
    client = get_client()
    result = client.table("profiles").select("user_id").eq("share_code", share_code).execute()
    return result.data[0]["user_id"] if result.data else None
