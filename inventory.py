class Inventory:
    def __init__(self):
        self.items = set()

    def add_item(self, name):
        self.items.add(name.lower())

    def remove_item(self, name):
        self.items.discard(name.lower())

    def has_item(self, name):
        return name.lower() in self.items

    def list_items(self):
        return self.items