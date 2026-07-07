from supabase_client import get_client


def _fetch_all_cocktails():
    client = get_client()
    result = client.table("cocktails").select("id, name, instructions, cocktail_ingredients(name, amount)").execute()
    return result.data


def show_cocktail(name):
    name = name.lower()
    for cocktail in _fetch_all_cocktails():
        if cocktail["name"].lower() == name:
            lines = [f"{i['name']}: {i['amount']}" for i in cocktail["cocktail_ingredients"]]
            return {"name": cocktail["name"], "ingredients": lines, "instructions": cocktail["instructions"]}
    return None


def cocktail_statuses(inventory_names):
    statuses = []
    for cocktail in _fetch_all_cocktails():
        needed = [i["name"].lower() for i in cocktail["cocktail_ingredients"]]
        missing = [name for name in needed if name not in inventory_names]
        if not missing:
            state = "can_make"
        elif len(missing) == 1:
            state = "almost"
        else:
            state = "missing_many"
        statuses.append({"name": cocktail["name"], "state": state, "missing": missing})
    order = {"can_make": 0, "almost": 1, "missing_many": 2}
    statuses.sort(key=lambda s: (order[s["state"]], s["name"]))
    return statuses
