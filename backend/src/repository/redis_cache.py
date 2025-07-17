import asyncio

from typing import Type, TypeVar
import redis.asyncio as redis
import json
T = TypeVar("T")

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def set_cached(key: str, value) -> None:
    # Automatically serialize Pydantic models or lists of them
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    elif isinstance(value, list) and hasattr(value[0], "model_dump"):
        value = [v.model_dump() for v in value]
    await redis_client.set(key, json.dumps(value))

async def get_cached(key: str, model_cls: type[T]) -> T | list[T] | None:
    raw = await redis_client.get(key)
    if not raw:
        return None
    data = json.loads(raw)
    # If it's a list of objects (like list of BattlePets)
    if isinstance(data, list):
        return [model_cls.model_validate(item) for item in data]

    return model_cls.model_validate(data)

async def get_cached_list(key: str, model_cls: Type[T]) -> list[T] | None:
    raw = await redis_client.get(key)
    if not raw:
        return None
    data = json.loads(raw)

    if isinstance(data, list):
        return [model_cls.model_validate(item) for item in data]
    return model_cls.model_validate(data)


async def main():
    from src.core.models import BattlePet, Ability, PetType
    # Example usage

    dummy_pet = BattlePet(
        id=1,
        name="Test Pet",
        level=25,
        health=1500,
        power=300,
        speed=280,
        breed="P/P",
        abilities=[101, 102, 103],
        source="Test Source",
        type=PetType.BEAST,
        popularity=5,
        is_untameable=False
    )
    await set_cached(f"pet:{dummy_pet.id}", dummy_pet)
    cached_pet = await get_cached(f"pet:{dummy_pet.id}", BattlePet)
    print(cached_pet)  # Output: BattlePet object with id=1


    #await set_cached("example_key", {"name": "example", "value": 42})
    #cached_value = await get_cached("example_key")
    #print(cached_value)  # Output: {'name': 'example', 'value': 42}

if __name__ == "__main__":
    asyncio.run(main())
