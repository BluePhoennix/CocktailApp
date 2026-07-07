from supabase_client import get_client


def list_items(user_id):
    client = get_client()
    result = client.table("inventory_items").select("name").eq("user_id", user_id).execute()
    return {row["name"] for row in result.data}


def add_item(user_id, name):
    client = get_client()
    client.table("inventory_items").upsert(
        {"user_id": user_id, "name": name.lower()}, on_conflict="user_id,name"
    ).execute()


def remove_item(user_id, name):
    client = get_client()
    client.table("inventory_items").delete().eq("user_id", user_id).eq("name", name.lower()).execute()
