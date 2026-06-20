# rooms.py

from monsters import MONSTERS
from items import ITEMS

class Room:
    def __init__(
        self,
        id,
        name,
        short_desc,
        long_desc,
        exits=None,
        items=None,
        locked_exits=None,
        monsters=None,
        coords=None
    ):
        self.id = id
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.exits = exits or {}
        self.items = items or []
        self.locked_exits = locked_exits or {}
        self.monsters = monsters or []
        self.coords = coords or (0, 0, 0, "default")

    def to_dict(self):
        return {
            "items": self.items,
            "locked_exits": self.locked_exits,
            "monsters": [MONSTERS[m].to_dict() for m in self.monsters],
            "coords": self.coords,
        }

    def load_from_dict(self, data):
        self.items = data.get("items", [])
        self.locked_exits = data.get("locked_exits", {})

        # Load coordinates
        self.coords = tuple(data.get("coords", self.coords))

        # Load monsters
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
        short_desc="You are standing in a small foyer.",
        long_desc="You are standing in a small foyer. The wallpaper is peeling, and a hallway leads north.",
        exits={"north": "hallway"},
        items=["rusty_key_01"],
        coords=(0, 0, 0, "house")
    )

    hallway = Room(
        "hallway",
        "Hallway",
        short_desc="A narrow hallway stretches east and west.",
        long_desc="A narrow hallway stretches east and west. The floorboards creak underfoot, and the foyer lies to the south.",
        exits={"south": "foyer", "west": "kitchen", "east": None},
        items=[],
        locked_exits={"east": "unlock_study_door"},
        monsters=["goblin_01"],
        coords=(1, 0, 0, "house")
    )

    study = Room(
        "study",
        "Study",
        short_desc="A quiet study lined with books.",
        long_desc="A quiet study lined with dusty bookshelves. A single oil lamp flickers on a desk. The hallway is to the west.",
        exits={"west": "hallway"},
        items=["torch_01"],
        coords=(2, 0, 0, "house")
    )

    kitchen = Room(
        "kitchen",
        "Kitchen",
        short_desc="A cozy kitchen that smells faintly of coffee.",
        long_desc="A cozy kitchen with a warm, lingering smell of coffee. Pots and pans hang from a rack overhead. The hallway is to the east.",
        exits={"east": "hallway"},
        items=[],
        coords=(1, -1, 0, "house")
    )

    return {
        "foyer": foyer,
        "hallway": hallway,
        "study": study,
        "kitchen": kitchen,
    }
