# main.py

import json
import os

print("LocalMUD is starting...")

try:
    SAVE_FILE = "savegame.json"

    # ---------------------------------------------------------
    # Item Definitions
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Core Data Structures
    # ---------------------------------------------------------
    class Room:
        def __init__(self, id, name, description, exits=None, items=None, locked_exits=None):
            self.id = id
            self.name = name
            self.description = description
            self.exits = exits or {}
            self.items = items or []
            self.locked_exits = locked_exits or {}

        def to_dict(self):
            return {
                "items": self.items,
                "locked_exits": self.locked_exits
            }

        def load_from_dict(self, data):
            self.items = data.get("items", [])
            self.locked_exits = data.get("locked_exits", {})

    def default_stats():
        return {
            "str": 12,
            "dex": 11,
            "con": 14,
            "int": 10,
            "wis": 10,
            "cha": 10,
        }

    class Player:
        def __init__(self, starting_room):
            self.current_room_id = starting_room
            self.inventory = []
            self.stats = default_stats()
            self.max_hp = 10 + self.modifier("con") * 2
            self.hp = self.max_hp

        def modifier(self, stat_name):
            score = self.stats.get(stat_name, 10)
            return (score - 10) // 2

        def to_dict(self):
            return {
                "current_room_id": self.current_room_id,
                "inventory": self.inventory,
                "stats": self.stats,
                "hp": self.hp,
                "max_hp": self.max_hp
            }

        def load_from_dict(self, data):
            self.current_room_id = data.get("current_room_id", "foyer")
            self.inventory = data.get("inventory", [])
            self.stats = data.get("stats", default_stats())
            self.max_hp = data.get("max_hp", 10 + self.modifier("con") * 2)
            self.hp = data.get("hp", self.max_hp)

    class GameState:
        def __init__(self, rooms, player):
            self.rooms = rooms
            self.player = player
            self.running = True

        def to_dict(self):
            return {
                "player": self.player.to_dict(),
                "rooms": {rid: room.to_dict() for rid, room in self.rooms.items()}
            }

        def load_from_dict(self, data):
            if "player" in data:
                self.player.load_from_dict(data["player"])
            if "rooms" in data:
                for rid, rdata in data["rooms"].items():
                    if rid in self.rooms:
                        self.rooms[rid].load_from_dict(rdata)

    # ---------------------------------------------------------
    # World Builder
    # ---------------------------------------------------------
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
            locked_exits={"east": "unlock_study_door"}
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

        rooms = {
            "foyer": foyer,
            "hallway": hallway,
            "study": study,
            "kitchen": kitchen,
        }

        player = Player("foyer")
        return GameState(rooms, player)

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    def get_current_room(gs):
        return gs.rooms[gs.player.current_room_id]

    def find_item_by_name(name, item_ids):
        name = name.lower()
        for iid in item_ids:
            item = ITEMS[iid]
            if item.name.lower() == name:
                return iid
        return None

    def format_stat_line(label, score, mod):
        sign = "+" if mod >= 0 else ""
        return f"{label.upper():3} {score:2} ({sign}{mod})"

    # ---------------------------------------------------------
    # Save / Load Helpers
    # ---------------------------------------------------------
    def save_game(gs):
        data = gs.to_dict()
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return "Game saved."

    def load_game(gs):
        if not os.path.exists(SAVE_FILE):
            return "No save file found."

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        gs.load_from_dict(data)
        return "Game loaded."

    # ---------------------------------------------------------
    # Command Handlers
    # ---------------------------------------------------------
    def cmd_look(gs, arg):
        room = get_current_room(gs)
        text = f"{room.name}\n{room.description}\n"

        if room.items:
            item_names = ", ".join(ITEMS[i].name for i in room.items)
            text += f"You see here: {item_names}\n"

        exits = []
        for direction, target in room.exits.items():
            if target is None:
                exits.append(f"{direction} (locked)")
            else:
                exits.append(direction)

        if exits:
            text += "Exits: " + ", ".join(exits)
        else:
            text += "There are no obvious exits."

        return text

    def cmd_go(gs, direction):
        if not direction:
            return "Go where?"

        room = get_current_room(gs)

        if direction not in room.exits:
            return f"You can't go '{direction}' from here."

        if room.exits[direction] is None:
            return f"The way {direction} is locked."

        gs.player.current_room_id = room.exits[direction]
        return f"You go {direction}.\n\n{cmd_look(gs, '')}"

    def cmd_inventory(gs, arg):
        inv = gs.player.inventory
        if not inv:
            return "You are carrying nothing."
        names = ", ".join(ITEMS[i].name for i in inv)
        return f"You are carrying: {names}"

    def cmd_examine(gs, arg):
        if not arg:
            return "Examine what?"

        room = get_current_room(gs)
        inv = gs.player.inventory

        iid = find_item_by_name(arg, inv)
        if iid:
            return ITEMS[iid].description

        iid = find_item_by_name(arg, room.items)
        if iid:
            return ITEMS[iid].description

        return f"You see no '{arg}'."

    def cmd_take(gs, arg):
        if not arg:
            return "Take what?"

        room = get_current_room(gs)
        iid = find_item_by_name(arg, room.items)
        if not iid:
            return f"There is no '{arg}' here."

        room.items.remove(iid)
        gs.player.inventory.append(iid)
        return f"You take the {ITEMS[iid].name}."

    def cmd_drop(gs, arg):
        if not arg:
            return "Drop what?"

        inv = gs.player.inventory
        iid = find_item_by_name(arg, inv)
        if not iid:
            return f"You aren't carrying '{arg}'."

        gs.player.inventory.remove(iid)
        get_current_room(gs).items.append(iid)
        return f"You drop the {ITEMS[iid].name}."

    def cmd_use(gs, arg):
        if not arg:
            return "Use what?"

        inv = gs.player.inventory
        iid = find_item_by_name(arg, inv)
        if not iid:
            return f"You aren't carrying '{arg}'."

        item = ITEMS[iid]
        if not item.use_effect:
            return f"You can't use the {item.name}."

        room = get_current_room(gs)

        for direction, effect in list(room.locked_exits.items()):
            if effect == item.use_effect:
                room.exits[direction] = "study"
                del room.locked_exits[direction]
                return f"You use the {item.name}. You hear a loud click — the door to the {direction} is now unlocked."

        return f"Using the {item.name} has no effect here."

    def cmd_stats(gs, arg):
        p = gs.player
        lines = []
        for label in ["str", "dex", "con", "int", "wis", "cha"]:
            score = p.stats.get(label, 10)
            mod = p.modifier(label)
            lines.append(format_stat_line(label, score, mod))
        lines.append(f"HP {p.hp}/{p.max_hp}")
        return "\n".join(lines)

    def cmd_quit(gs, arg):
        gs.running = False
        return "Goodbye."

    def cmd_help(gs, arg):
        return (
            "Available commands:\n"
            "  look / l\n"
            "  go <direction>\n"
            "  examine <item>\n"
            "  take <item>\n"
            "  drop <item>\n"
            "  use <item>\n"
            "  inventory / i\n"
            "  stats\n"
            "  save\n"
            "  load\n"
            "  quit / exit\n"
            "  help\n"
        )

    def cmd_save(gs, arg):
        return save_game(gs)

    def cmd_load(gs, arg):
        return load_game(gs)

    # ---------------------------------------------------------
    # Command Registry
    # ---------------------------------------------------------
    COMMANDS = {
        "look": cmd_look,
        "l": cmd_look,
        "go": cmd_go,
        "move": cmd_go,
        "inventory": cmd_inventory,
        "inv": cmd_inventory,
        "i": cmd_inventory,
        "examine": cmd_examine,
        "x": cmd_examine,
        "take": cmd_take,
        "get": cmd_take,
        "drop": cmd_drop,
        "use": cmd_use,
        "stats": cmd_stats,
        "quit": cmd_quit,
        "exit": cmd_quit,
        "help": cmd_help,
        "?": cmd_help,
        "save": cmd_save,
        "load": cmd_load,
    }

    # ---------------------------------------------------------
    # Parser + Dispatcher
    # ---------------------------------------------------------
    def parse_command(cmd):
        cmd = cmd.strip().lower()
        if not cmd:
            return "", ""
        parts = cmd.split(maxsplit=1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    def dispatch(cmd, gs):
        verb, arg = parse_command(cmd)

        if verb == "":
            return "You must type something."

        if verb in COMMANDS:
            return COMMANDS[verb](gs, arg)

        return f"Unknown command: '{verb}'. Type 'help' for a list of commands."

    # ---------------------------------------------------------
    # Main Game Loop
    # ---------------------------------------------------------
    def main():
        gs = build_world()

        print("Welcome to LocalMUD (Minimal Core).")
        print("Type 'help' for commands.\n")
        print(cmd_look(gs, ""))

        while gs.running:
            command = input("\n> ")
            print()
            print(dispatch(command, gs))

    if __name__ == "__main__":
        main()

except Exception:
    import traceback
    print("\n--- CRASH DETECTED ---")
    traceback.print_exc()
    input("\nPress Enter to exit...")
