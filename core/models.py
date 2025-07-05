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
    name: str = Field(..., description="Name of the ability")
    damage: str = Field(..., description="Damage dealt by the ability")
    healing: str = Field(..., description="Healing provided by the ability")
    duration: str = Field(..., description="Duration of the ability effect")
    cooldown: str = Field(..., description="Cooldown time for the ability")
    accuracy: str = Field(..., description="Accuracy of the ability")
    type: PetType = Field(..., description="Type of the ability")
    popularity: int = Field(..., description="Popularity rating of the ability")

class BattlePet(BaseModel):
    """Represents a battle pet with its attributes."""
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    name: str = Field(..., description="Name of the battle pet")
    level: int = Field(..., description="Level of the battle pet")
    health: int = Field(..., description="Health of the battle pet")
    power: int = Field(..., description="Power of the battle pet")
    speed: int = Field(..., description="Speed of the battle pet")
    breed: str = Field(..., description="Breed of the battle pet")
    abilities: int = Field(..., description="List of abilities of the battle pet, max 6 abilities")
    source: str = Field(..., description="Source of the battle pet")
    type: PetType = Field(..., description="Type of the battle pet")
    popularity: int = Field(..., description="Popularity rating of the battle pet")
    is_untameable: bool = Field(..., description="Whether the battle pet is untameable")

    @field_validator("abilities")
    @classmethod
    def ensure_six_abilities(cls, v: list[str]) -> list[str]:
        if len(v) < 6:
            # Pad with empty abilities
            empty_ability = "Unknown"
            v += [empty_ability] * (6 - len(v))
        elif len(v) > 6:
            v = v[:6]
        return v


