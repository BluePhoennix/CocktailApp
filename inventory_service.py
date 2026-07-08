from supabase_client import get_client


def list_items(user_id):
    client = get_client()
    result = client.table("inventory_items").select("name, category").eq("user_id", user_id).execute()
    return result.data


def add_item(user_id, name, category):
    client = get_client()
    client.table("inventory_items").upsert(
        {"user_id": user_id, "name": name.lower(), "category": category}, on_conflict="user_id,name"
    ).execute()


def remove_item(user_id, name):
    client = get_client()
    client.table("inventory_items").delete().eq("user_id", user_id).eq("name", name.lower()).execute()
