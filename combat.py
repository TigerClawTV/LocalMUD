
# combat.py

import random

def player_attack(gs, monster):
    """Handles the player's attack against a monster."""
    roll = random.randint(1, 20)
    total = roll + gs.player.modifier("str")

    hit = total >= monster.ac
    dmg = 0

    if hit:
        dmg = random.randint(1, 6) + gs.player.modifier("str")
        dmg = max(1, dmg)
        monster.hp -= dmg

    return {
        "roll": roll,
        "total": total,
        "hit": hit,
        "damage": dmg,
        "monster_dead": monster.hp <= 0
    }


def monster_attack(gs, monster):
    """Handles the monster attacking the player."""
    roll = random.randint(1, 20)
    total = roll + monster.attack_bonus

    player_ac = 10 + gs.player.modifier("dex")
    hit = total >= player_ac
    dmg = 0

    if hit:
        dmg = random.randint(1, monster.damage_die)
        gs.player.hp -= dmg

    return {
        "roll": roll,
        "total": total,
        "hit": hit,
        "damage": dmg,
        "player_dead": gs.player.hp <= 0
    }


def monster_free_attack(gs, monster):
    """Used by WAIT — monster gets a free attack."""
    return monster_attack(gs, monster)
