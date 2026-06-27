

# world/region_house.py

from rooms import Room

def load_house():
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
