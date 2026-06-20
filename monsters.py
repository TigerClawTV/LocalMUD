
# monsters.py

class Monster:
    def __init__(self, id, name, description, hp, ac, attack_bonus, damage_die, exp_reward, gold_reward):
        self.id = id
        self.name = name
        self.description = description
        self.hp = hp
        self.ac = ac
        self.attack_bonus = attack_bonus
        self.damage_die = damage_die
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def to_dict(self):
        return {
            "id": self.id,
            "hp": self.hp
        }

    def load_from_dict(self, data):
        self.hp = data.get("hp", self.hp)


# Global monster registry
MONSTERS = {
    "goblin_01": Monster(
        "goblin_01",
        "goblin",
        "A small, wiry goblin with sharp teeth and a nasty grin.",
        hp=6,
        ac=12,
        attack_bonus=2,
        damage_die=6,
        exp_reward=15,
        gold_reward=5
    )
}
