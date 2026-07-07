from CocktailApp.recipes import COCKTAILS
def search(item):
    results = []
    for cocktail in COCKTAILS:
        if item.lower() in cocktail.lower():
            results.append(cocktail)
    return results

def show_cocktail(name):
    name = name.lower()
    for cocktail_name in COCKTAILS:
        if cocktail_name.lower() == name:
            cocktail = COCKTAILS[cocktail_name]
            ingredients = [f"{ingredient['name']}: {ingredient['amount']}" for ingredient in cocktail["ingredients"]]
            instructions = cocktail["instructions"]
            return "\n" + name + ":\n" + f"\n".join(ingredients) + "\n" + "Instructions: " + instructions + "\n"
    return "Cocktail not found."

def can_make(name, inventory):
    name = name.lower()

    for cocktail_name in COCKTAILS:
        if cocktail_name.lower() == name:
            cocktail = COCKTAILS[cocktail_name]
            for ingredient in cocktail["ingredients"]:
                if ingredient["name"].lower() not in inventory.list_items():
                     return False
            return True
    return False

def possible_cocktails(inventory):
    possible = []
    for cocktail in COCKTAILS:
        if can_make(cocktail, inventory):
            possible.append(cocktail)
    return possible

def close_cocktails(inventory):
    close = []
    for cocktail in COCKTAILS:
        if cocktail not in possible_cocktails(inventory):
            cocktail_ingredients = [ingredient["name"].lower() for ingredient in COCKTAILS[cocktail]["ingredients"]]
            missing = [ingredient for ingredient in cocktail_ingredients if ingredient not in inventory.list_items()]
            if len(missing) == 1:
                close.append((cocktail, missing[0]))
    return close

def ingredients_needed(inventory):
    almost = close_cocktails(inventory)
    for cocktail in COCKTAILS:
        if cocktail in almost:
            for ingredient in COCKTAILS[cocktail]["ingredients"]:
                if ingredient["name"].lower() not in inventory.list_items():
                    print(cocktail + " is missing: " + ingredient["name"])