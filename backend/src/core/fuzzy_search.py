from fuzzywuzzy import process as wuzzy_process
from src.core.models import Ability


async def fuzzy_search_wuzzy(query: str, abilities: list[Ability]) -> list[Ability]:
    lookup = {a.fuzz_search_data: a for a in abilities}
    choices = list(lookup.keys())

    matches = wuzzy_process.extract(query, choices, limit=20)
    for match in matches:
        print(match)
    results = [
        lookup[match_str]
        for match_str, score in matches
        if score >= 50
    ]

    return results

from rapidfuzz import process as rapid_process, fuzz as rapid_fuzz
async def fuzzy_search_rapid(
    query: str,
    abilities: list[Ability],
    *,
    limit: int = 5,
    min_score: int = 30,
) -> list[Ability]:
    texts = [a.fuzz_search_data for a in abilities]

    matches = rapid_process.extract(
        query,
        texts,
        scorer=rapid_fuzz.WRatio,
        limit=limit,
    )
    for m in matches:
        print(m)

    return [
        abilities[idx]
        for _, score, idx in matches
        if score >= min_score
    ]

