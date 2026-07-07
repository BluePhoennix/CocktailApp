from supabase_client import get_client


def _fetch_all_cocktails():
    client = get_client()
    result = client.table("cocktails").select("id, name, instructions, cocktail_ingredients(name, amount)").execute()
    return result.data


def search(query):
    query = query.lower()
    return [c["name"] for c in _fetch_all_cocktails() if query in c["name"].lower()]


def show_cocktail(name):
    name = name.lower()
    for cocktail in _fetch_all_cocktails():
        if cocktail["name"].lower() == name:
            lines = [f"{i['name']}: {i['amount']}" for i in cocktail["cocktail_ingredients"]]
            return {"name": cocktail["name"], "ingredients": lines, "instructions": cocktail["instructions"]}
    return None


def _can_make(cocktail, inventory_names):
    needed = [i["name"].lower() for i in cocktail["cocktail_ingredients"]]
    return all(name in inventory_names for name in needed)


def possible_cocktails(inventory_names):
    return [c["name"] for c in _fetch_all_cocktails() if _can_make(c, inventory_names)]


def close_cocktails(inventory_names):
    close = []
    for cocktail in _fetch_all_cocktails():
        if not _can_make(cocktail, inventory_names):
            needed = [i["name"].lower() for i in cocktail["cocktail_ingredients"]]
            missing = [name for name in needed if name not in inventory_names]
            if len(missing) == 1:
                close.append((cocktail["name"], missing[0]))
    return close
