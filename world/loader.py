# world/loader.py

from world.region_house import load_house
# from world.region_forest import load_forest
# from world.region_city import load_city
# from world.region_dungeon import load_dungeon
# Add more regions here as you create them


def load_all_regions():
    """
    Loads every region module and merges their room dictionaries
    into a single world dictionary.

    Returns:
        dict: { room_id: Room }
    """

    world = {}

    # List of region loader functions
    region_loaders = [
        load_house,
        # load_forest,
        # load_city,
        # load_dungeon,
    ]

    for loader in region_loaders:
        region_rooms = loader()

        # Collision detection: duplicate room IDs across regions
        for rid in region_rooms:
            if rid in world:
                raise ValueError(
                    f"Duplicate room ID detected: '{rid}' appears in multiple regions."
                )

        world.update(region_rooms)

    return world
