# rooms.py

from monsters import MONSTERS
from items import ITEMS

class Room:
    def __init__(self, id, name, description, exits=None, items=None, locked_exits=None, monsters=None):
        self.id = id
        self.name = name
        self.description = description
        self.exits = exits or {}
        self.items = items or []
        self.locked_exits = locked_exits or {}
        self.monsters = monsters or []

    def to_dict(self):
        return {
            "items": self.items,
            "locked_exits": self.locked_exits,
            "monsters": [MONSTERS[m].to_dict() for m in self.monsters]
        }

    def load_from_dict(self, data):
        self.items = data.get("items", [])
        self.locked_exits = data.get("locked_exits", {})

        monster_data = data.get("monsters", [])
        self.monsters = []
        for mdata in monster_data:
            mid = mdata["id"]
            if mid in MONSTERS:
                MONSTERS[mid].load_from_dict(mdata)
                self.monsters.append(mid)


def build_world():
    foyer = Room(
        "foyer",
        "Foyer",
        "You are standing in a small foyer. A hallway leads north.",
        {"north": "hallway"},
        items=["rusty_key_01"]
    )

    hallway = Room(
        "hallway",
        "Hallway",
        "A narrow hallway stretches east and west. The foyer is south.",
        {"south": "foyer", "west": "kitchen", "east": None},
        items=[],
        locked_exits={"east": "unlock_study_door"},
        monsters=["goblin_01"]
    )

    study = Room(
        "study",
        "Study",
        "A quiet study lined with books. The hallway is to the west.",
        {"west": "hallway"},
        items=["torch_01"]
    )

    kitchen = Room(
        "kitchen",
        "Kitchen",
        "A cozy kitchen that smells faintly of coffee. The hallway is to the east.",
        {"east": "hallway"},
        items=[]
    )

    return {
        "foyer": foyer,
        "hallway": hallway,
        "study": study,
        "kitchen": kitchen,
    }

