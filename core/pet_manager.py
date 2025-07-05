from repository.mongo_db import MongoDb
from repository.interface import DbBase
from core.models import BattlePet, Ability, PetType

class PetManager:
    def __init__(self, db: DbBase = MongoDb()) -> None:
        self.db = db
        #self.db.populate_battle_pets("data/mop_battle_pets.csv")a

    def list_battle_pets(self, pet_type: PetType = None) -> list[BattlePet]:
        """List all battle pets in the database."""
        return self.db.get_all_battle_pets()
    def find_attack_counters(self, pet_name

    def find_defense_counters
