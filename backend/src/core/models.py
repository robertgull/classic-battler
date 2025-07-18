from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator

# types: Aquatic # Beast # Critter # Dragonkin # Elemental # Flying # Humanoid # Magic # Mechanical # Undead


class PetType(str, Enum):
    AQUATIC = "Aquatic"
    BEAST = "Beast"
    CRITTER = "Critter"
    DRAGONKIN = "Dragonkin"
    ELEMENTAL = "Elemental"
    FLYING = "Flying"
    HUMANOID = "Humanoid"
    MAGIC = "Magic"
    MECHANICAL = "Mechanical"
    UNDEAD = "Undead"


# "Name", "Damage", "Healing", "Duration", "Cooldown", "Accuracy", "Type", "Popularity"
class Ability(BaseModel):
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, BattlePet) and self.id == other.id

    def __str__(self):
        parts = [
            f"{self.name} ({self.id})",
            f"Type: {self.type}",
            f"Damage: {self.damage}",
            f"Healing: {self.healing}",
            f"Duration: {self.duration}",
            f"Cooldown: {self.cooldown}",
            f"Accuracy: {self.accuracy}",
            f"Popularity: {self.popularity}",
            f"Description: {self.description}",
        ]
        return ". ".join(parts)

    id: int = Field(..., description="Unique identifier for the ability")
    name: str = Field(..., description="Name of the ability")
    damage: str = Field(..., description="Damage dealt by the ability")
    healing: str = Field(..., description="Healing provided by the ability")
    duration: str = Field(..., description="Duration of the ability effect")
    cooldown: str = Field(..., description="Cooldown time for the ability")
    accuracy: str = Field(..., description="Accuracy of the ability")
    type: PetType = Field(..., description="Type of the ability")
    popularity: int = Field(..., description="Popularity rating of the ability")
    description: str = Field(..., description="Description of the ability")


class BattlePet(BaseModel):
    """Represents a battle pet with its attributes."""

    def __str__(self):
        parts = [
            f"{self.name} (ID: {self.id})",
            f"Level: {self.level}",
            f"Health: {self.health}",
            f"Power: {self.power}",
            f"Speed: {self.speed}",
            f"Breed: {self.breed}",
            f"Source: {self.source}",
            f"Type: {self.type}",
            f"Popularity: {self.popularity}",
            f"Untameable: {'Yes' if self.is_untameable else 'No'}",
        ]
        return ". ".join(parts)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, BattlePet) and self.id == other.id

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: int = Field(..., description="Unique identifier for the battle pet")
    name: str = Field(..., description="Name of the battle pet")
    level: int = Field(..., description="Level of the battle pet")
    health: int = Field(..., description="Health of the battle pet")
    power: int = Field(..., description="Power of the battle pet")
    speed: int = Field(..., description="Speed of the battle pet")
    breed: str = Field(..., description="Breed of the battle pet")
    abilities: list[int] = Field(
        ..., description="List of abilities of the battle pet, max 6 abilities"
    )
    source: str = Field(..., description="Source of the battle pet")
    type: PetType = Field(..., description="Type of the battle pet")
    popularity: int = Field(..., description="Popularity rating of the battle pet")
    is_untameable: bool = Field(..., description="Whether the battle pet is untameable")

    @field_validator("abilities")
    @classmethod
    def ensure_six_abilities(cls, v: list[int]) -> list[int]:
        if len(v) < 6:
            empty_ability = -1
            v += [empty_ability] * (6 - len(v))
        elif len(v) > 6:
            v = v[:6]
        return v
