
# items.py

class Item:
    def __init__(self, id, name, description, use_effect=None):
        self.id = id
        self.name = name
        self.description = description
        self.use_effect = use_effect

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "use_effect": self.use_effect
        }

    @staticmethod
    def from_dict(data):
        return Item(
            data["id"],
            data["name"],
            data["description"],
            data.get("use_effect")
        )


# Global item registry
ITEMS = {
    "rusty_key_01": Item(
        "rusty_key_01",
        "rusty key",
        "A corroded iron key. It looks like it might still work.",
        use_effect="unlock_study_door"
    ),
    "torch_01": Item(
        "torch_01",
        "torch",
        "A wooden torch. It is unlit."
    ),
}
