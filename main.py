from functions import possible_cocktails, show_cocktail, search, close_cocktails
from inventory import Inventory

inventory = Inventory()

while True:
    print("\n--- Cocktail App ---")
    print("1. Add ingredient")
    print("2. Remove ingredient")
    print("3. View inventory")
    print("4. Search cocktails")
    print("5. What can I make?")
    print("6. What am I close to making?")
    print("7. Exit")

    choice = input("\nChoose: ")

    if choice == "1":
        addition = input("Enter ingredient to add: ")
        inventory.add_item(addition)

    elif choice == "2":
        removal = input("Enter ingredient to remove: ")
        inventory.remove_item(removal)

    elif choice == "3":
        print("Inventory: \n")
        for item in inventory.list_items():
            print(item)

    elif choice == "4":
        print("Enter cocktail name (or 'exit' to quit):")
        user_input = input()
        if user_input.lower() == "exit":
            break
        for item in search(user_input):
            print(item)
        print("Enter cocktail name to see details:")
        detail_input = input()
        print(show_cocktail(detail_input))
    
    elif choice == "5":
        possible = possible_cocktails(inventory)
        if len(possible) == 0:
            print("You can't make any cocktails with your current inventory.")
        else:
            print("Cocktails you can make: \n")
            for cocktail in possible_cocktails(inventory):
                print(cocktail)
    
    elif choice == "6":
        close = close_cocktails(inventory)
        if len(close) == 0:
            print("You are not close to making any cocktails.")
        else:
            print("Cocktails you are close to making: \n")
            for cocktail, missing in close_cocktails(inventory):
                print(f"{cocktail} is missing: {missing}")

    else:
        break