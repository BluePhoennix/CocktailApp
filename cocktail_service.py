from supabase_client import get_client


def _fetch_all_cocktails(user_id):
    client = get_client()
    result = (
        client.table("cocktails")
        .select("id, name, instructions, cocktail_ingredients(name, amount)")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data


def create_cocktail(user_id, name, instructions, ingredients):
    client = get_client()
    result = client.table("cocktails").insert(
        {"user_id": user_id, "name": name, "instructions": instructions}
    ).execute()
    cocktail_id = result.data[0]["id"]
    rows = [{"cocktail_id": cocktail_id, "name": ing["name"], "amount": ing["amount"]} for ing in ingredients]
    client.table("cocktail_ingredients").insert(rows).execute()


def get_cocktail(user_id, cocktail_id):
    client = get_client()
    result = (
        client.table("cocktails")
        .select("id, name, instructions, cocktail_ingredients(name, amount)")
        .eq("id", cocktail_id)
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_cocktail(user_id, cocktail_id, name, instructions, ingredients):
    client = get_client()
    result = (
        client.table("cocktails")
        .update({"name": name, "instructions": instructions})
        .eq("id", cocktail_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        return False

    client.table("cocktail_ingredients").delete().eq("cocktail_id", cocktail_id).execute()
    rows = [{"cocktail_id": cocktail_id, "name": ing["name"], "amount": ing["amount"]} for ing in ingredients]
    client.table("cocktail_ingredients").insert(rows).execute()
    return True


def delete_cocktail(user_id, cocktail_id):
    client = get_client()
    client.table("cocktails").delete().eq("id", cocktail_id).eq("user_id", user_id).execute()


def cocktail_statuses(user_id, inventory_names):
    statuses = []
    for cocktail in _fetch_all_cocktails(user_id):
        ingredients = []
        missing = []
        for ing in cocktail["cocktail_ingredients"]:
            have = ing["name"].lower() in inventory_names
            if not have:
                missing.append(ing["name"])
            ingredients.append({"name": ing["name"], "amount": ing["amount"], "have": have})

        if not missing:
            state = "can_make"
        elif len(missing) == 1:
            state = "almost"
        else:
            state = "missing_many"

        statuses.append({
            "id": cocktail["id"],
            "name": cocktail["name"],
            "state": state,
            "ingredients": ingredients,
            "instructions": cocktail["instructions"],
        })

    order = {"can_make": 0, "almost": 1, "missing_many": 2}
    statuses.sort(key=lambda s: (order[s["state"]], s["name"]))
    return statuses
