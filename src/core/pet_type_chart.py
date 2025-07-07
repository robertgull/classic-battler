from src.core.models import PetType

pet_type_matrix = {
    PetType.AQUATIC: {
        "strong_against": [PetType.ELEMENTAL],
        "weak_against": [PetType.MAGIC],
    },
    PetType.BEAST: {
        "strong_against": [PetType.CRITTER],
        "weak_against": [PetType.FLYING],
    },
    PetType.CRITTER: {
        "strong_against": [PetType.UNDEAD],
        "weak_against": [PetType.HUMANOID],
    },
    PetType.DRAGONKIN: {
        "strong_against": [PetType.MAGIC],
        "weak_against": [PetType.UNDEAD],
    },
    PetType.ELEMENTAL: {
        "strong_against": [PetType.MECHANICAL],
        "weak_against": [PetType.CRITTER],
    },
    PetType.FLYING: {
        "strong_against": [PetType.AQUATIC],
        "weak_against": [PetType.DRAGONKIN],
    },
    PetType.HUMANOID: {
        "strong_against": [PetType.DRAGONKIN],
        "weak_against": [PetType.BEAST],
    },
    PetType.MAGIC: {
        "strong_against": [PetType.FLYING],
        "weak_against": [PetType.MECHANICAL],
    },
    PetType.MECHANICAL: {
        "strong_against": [PetType.BEAST],
        "weak_against": [PetType.ELEMENTAL],
    },
    PetType.UNDEAD: {
        "strong_against": [PetType.HUMANOID],
        "weak_against": [PetType.AQUATIC],
    },
}
